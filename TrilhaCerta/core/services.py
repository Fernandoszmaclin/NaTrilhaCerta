"""Camada de serviços — encapsula regras de negócio fora das views.

Cada função lança exceções de domínio (DomainError) com mensagens prontas
para o usuário; as views só traduzem para JsonResponse.
"""

from __future__ import annotations

import logging
import uuid

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Expedicao, FichaMedica, Pagamento, Reserva

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Erro de regra de negócio — mensagem segura para exibir ao usuário."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


# ─────────────────────────────  Autenticação  ─────────────────────────────

def autenticar_usuario(request, username: str, password: str) -> User:
    user = authenticate(request, username=username, password=password)
    if user is None or user.is_staff or user.is_superuser:
        # Bloqueia admin no modal por segurança.
        raise DomainError('Usuário ou senha incorretos.')
    login(request, user)
    logger.info('Login bem-sucedido: user_id=%s', user.id)
    return user


def criar_usuario(request, dados: dict) -> User:
    # Aplica as mesmas políticas de senha do AUTH_PASSWORD_VALIDATORS
    # (o form não as executa automaticamente).
    try:
        validate_password(dados['password'])
    except ValidationError as exc:
        raise DomainError(' '.join(exc.messages)) from exc

    user = User.objects.create_user(
        username=dados['username'],
        email=dados['email'],
        password=dados['password'],
        first_name=dados.get('first_name', ''),
        last_name=dados.get('last_name', ''),
    )
    login(request, user)
    logger.info('Cadastro concluído: user_id=%s', user.id)
    return user


# ─────────────────────────────  Reservas / Checkout  ─────────────────────────────

def _get_expedicao(expedicao_id: int) -> Expedicao:
    try:
        return Expedicao.objects.get(id=expedicao_id)
    except Expedicao.DoesNotExist as exc:
        raise DomainError('Expedição não encontrada.', status=404) from exc


def iniciar_checkout(usuario: User, expedicao_id: int, quantidade_pessoas: int) -> Pagamento:
    """Cria Reserva + Pagamento pendente atomicamente."""
    with transaction.atomic():
        # Lock da linha da expedição evita overbooking sob concorrência:
        # a checagem de vagas e a criação da reserva ficam serializadas.
        try:
            expedicao = Expedicao.objects.select_for_update().get(id=expedicao_id)
        except Expedicao.DoesNotExist as exc:
            raise DomainError('Expedição não encontrada.', status=404) from exc

        if expedicao.vagas_disponiveis < quantidade_pessoas:
            raise DomainError('Não há vagas suficientes. Tente entrar na lista de espera.')

        reserva = Reserva.objects.create(
            usuario=usuario,
            expedicao=expedicao,
            quantidade_pessoas=quantidade_pessoas,
            status='pendente',
        )
        pagamento = Pagamento.objects.create(
            reserva=reserva,
            metodo_pagamento='pix',
            valor_total=reserva.valor_total,
            status='pendente',
            gateway_id=f'sim_mp_{uuid.uuid4().hex[:8]}',
            qr_code_pix='00020126360014BR.GOV.BCB.PIX.SIMULADO...',
        )
    logger.info('Checkout iniciado: reserva_id=%s pagamento_id=%s', reserva.id, pagamento.id)
    return pagamento


def entrar_lista_espera(usuario: User, expedicao_id: int) -> Reserva:
    expedicao = _get_expedicao(expedicao_id)

    with transaction.atomic():
        # Lock por usuário+expedição evita inscrições duplicadas concorrentes.
        ja_existe = (
            Reserva.objects
            .select_for_update()
            .filter(usuario=usuario, expedicao=expedicao)
            .exclude(status='cancelada')
            .exists()
        )
        if ja_existe:
            raise DomainError('Você já possui uma reserva ou já está na fila para esta expedição.')

        return Reserva.objects.create(
            usuario=usuario,
            expedicao=expedicao,
            quantidade_pessoas=1,
            status='lista_espera',
        )


def cancelar_reserva(usuario: User, reserva_id: int) -> Reserva:
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=usuario)
    except Reserva.DoesNotExist as exc:
        raise DomainError('Reserva não encontrada.', status=404) from exc

    if reserva.status in ('cancelada', 'concluida'):
        raise DomainError('Esta reserva não pode ser cancelada.')

    with transaction.atomic():
        reserva.status = 'cancelada'
        reserva.save(update_fields=['status'])

        pagamento_aprovado = reserva.pagamentos.filter(status='aprovado').first()
        if pagamento_aprovado:
            # TODO: integrar refund real do gateway.
            pagamento_aprovado.status = 'estornado'
            pagamento_aprovado.save(update_fields=['status'])
        else:
            reserva.pagamentos.filter(status='pendente').update(status='recusado')

    logger.info('Reserva cancelada: reserva_id=%s', reserva.id)
    return reserva


def salvar_ficha_medica(usuario: User, reserva_id: int, dados: dict) -> FichaMedica:
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=usuario)
    except Reserva.DoesNotExist as exc:
        raise DomainError('Reserva não encontrada.', status=404) from exc

    if reserva.status not in ('confirmada', 'confirmada_e_pronta'):
        raise DomainError('A ficha médica só pode ser preenchida para reservas confirmadas.')

    with transaction.atomic():
        # Bloqueia a reserva para contar as fichas existentes de forma consistente.
        reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)

        if reserva.fichas_medicas.count() >= reserva.quantidade_pessoas:
            raise DomainError('Todas as fichas médicas desta reserva já foram preenchidas.')

        ficha = FichaMedica.objects.create(
            reserva=reserva,
            nome_completo=dados.get('nome_completo') or usuario.get_full_name() or usuario.username,
            restricoes_alimentares=dados.get('restricoes_alimentares', ''),
            tipo_sanguineo=dados.get('tipo_sanguineo', ''),
            contato_emergencia=dados.get('contato_emergencia', ''),
        )

        # Só marca como pronta quando todas as fichas obrigatórias foram preenchidas.
        if reserva.fichas_medicas.count() >= reserva.quantidade_pessoas:
            reserva.status = 'confirmada_e_pronta'
            reserva.save(update_fields=['status'])

    logger.info('Ficha médica salva: reserva_id=%s', reserva.id)
    return ficha


# ─────────────────────────────  Webhook  ─────────────────────────────

def verificar_assinatura_webhook(payload: bytes, signature: str, secret: str) -> bool:
    """Validação HMAC-SHA256 padrão para webhooks (Stripe-style)."""
    import hashlib
    import hmac

    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def processar_webhook_pagamento(gateway_id: str, novo_status: str) -> None:
    try:
        pagamento = Pagamento.objects.select_related('reserva').get(gateway_id=gateway_id)
    except Pagamento.DoesNotExist as exc:
        raise DomainError('Pagamento não encontrado', status=404) from exc

    # Idempotência: estados finais não são reprocessados.
    if pagamento.status in ('aprovado', 'recusado', 'estornado'):
        logger.info('Webhook ignorado (já processado): gateway_id=%s', gateway_id)
        return

    with transaction.atomic():
        if novo_status == 'approved':
            pagamento.status = 'aprovado'
            pagamento.reserva.status = 'confirmada'
        elif novo_status == 'rejected':
            pagamento.status = 'recusado'
            pagamento.reserva.status = 'cancelada'
        else:
            raise DomainError('Status inválido.')
        pagamento.save(update_fields=['status'])
        pagamento.reserva.save(update_fields=['status'])

    logger.info('Webhook processado: gateway_id=%s novo_status=%s', gateway_id, novo_status)
