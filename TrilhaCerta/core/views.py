"""Views finas: parsing, autorização e tradução de DomainError → JsonResponse."""

import json
import logging

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import services
from .forms import (
    CheckoutForm,
    FichaMedicaForm,
    ListaEsperaForm,
    LoginForm,
    SignupForm,
)
from .models import Expedicao, Reserva
from .services import DomainError

logger = logging.getLogger(__name__)


# ─────────────────────────────  Helpers  ─────────────────────────────

def _payload(request) -> dict:
    """Lê JSON body ou cai em form-encoded sem estourar exceção."""
    try:
        return json.loads(request.body or b'{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return request.POST.dict()


def _form_error(form) -> str:
    """Pega a primeira mensagem de erro do form para retorno JSON."""
    for errors in form.errors.values():
        if errors:
            return errors[0]
    return 'Dados inválidos.'


def _domain_error(exc: DomainError, *, success_key: str = 'success') -> JsonResponse:
    return JsonResponse({success_key: False, 'message': exc.message}, status=exc.status)


def _rate_limited(request, scope: str, *, limit: int = 10, window: int = 300) -> bool:
    """Throttle simples por IP via cache. True = limite excedido.

    Mitiga brute force em endpoints sensíveis sem dependência externa.
    Para múltiplos processos/instâncias, configure um CACHES compartilhado (Redis).
    """
    ip = request.META.get('REMOTE_ADDR', 'desconhecido')
    key = f'ratelimit:{scope}:{ip}'
    tentativas = cache.get(key, 0)
    if tentativas >= limit:
        return True
    cache.set(key, tentativas + 1, window)
    return False


# ─────────────────────────────  Páginas  ─────────────────────────────

def home(request):
    hoje = timezone.now().date()
    expedicoes = (
        Expedicao.objects
        .filter(ativa=True, data_inicio__gte=hoje)
        .prefetch_related('imagens', 'reservas')
        .order_by('data_inicio')[:6]
    )
    return render(request, 'index.html', {'expedicoes': expedicoes})


def expedicoes_lista(request):
    hoje = timezone.now().date()
    expedicoes = (
        Expedicao.objects
        .filter(ativa=True, data_inicio__gte=hoje)
        .prefetch_related('imagens', 'reservas')
        .order_by('data_inicio')
    )
    return render(request, 'expedicoes.html', {'expedicoes': expedicoes})


def contato(request):
    return render(request, 'contato.html')


# ─────────────────────────────  Autenticação  ─────────────────────────────

@require_POST
def login_view(request):
    if _rate_limited(request, 'login', limit=10, window=300):
        return JsonResponse(
            {'success': False, 'message': 'Muitas tentativas. Tente novamente em alguns minutos.'},
            status=429,
        )
    form = LoginForm(_payload(request))
    if not form.is_valid():
        return JsonResponse({'success': False, 'message': _form_error(form)}, status=400)
    try:
        user = services.autenticar_usuario(request, **form.cleaned_data)
    except DomainError as exc:
        return _domain_error(exc)
    return JsonResponse({
        'success': True,
        'message': f'Bem-vindo de volta, {user.first_name or user.username}!',
        'username': user.first_name or user.username,
    })


@require_POST
def signup_view(request):
    if _rate_limited(request, 'signup', limit=10, window=3600):
        return JsonResponse(
            {'success': False, 'message': 'Muitas tentativas. Tente novamente mais tarde.'},
            status=429,
        )
    form = SignupForm(_payload(request))
    if not form.is_valid():
        return JsonResponse({'success': False, 'message': _form_error(form)}, status=400)
    user = services.criar_usuario(request, form.cleaned_data)
    return JsonResponse({
        'success': True,
        'message': f'Conta criada com sucesso! Bem-vindo, {user.first_name}!',
        'username': user.first_name,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')


# ─────────────────────────────  Checkout & reservas  ─────────────────────────────

@require_POST
@login_required
def checkout_view(request):
    form = CheckoutForm(_payload(request))
    if not form.is_valid():
        return JsonResponse({'success': False, 'message': _form_error(form)}, status=400)
    try:
        pagamento = services.iniciar_checkout(request.user, **form.cleaned_data)
    except DomainError as exc:
        return _domain_error(exc)
    except Exception:
        logger.exception('Erro inesperado no checkout')
        return JsonResponse({'success': False, 'message': 'Erro interno.'}, status=500)

    return JsonResponse({
        'success': True,
        'message': 'Reserva gerada. Aguardando pagamento do PIX.',
        'pagamento_id': str(pagamento.id),
        'qr_code_pix': pagamento.qr_code_pix,
        'valor_total': str(pagamento.valor_total),
        'vencimento': '15 minutos',
    })


@require_POST
@login_required
def entrar_lista_espera(request):
    form = ListaEsperaForm(_payload(request))
    if not form.is_valid():
        return JsonResponse({'success': False, 'message': _form_error(form)}, status=400)
    try:
        services.entrar_lista_espera(request.user, form.cleaned_data['expedicao_id'])
    except DomainError as exc:
        return _domain_error(exc)
    return JsonResponse({
        'success': True,
        'message': 'Sucesso! Você entrou na lista de espera. Avisaremos via e-mail se uma vaga for liberada.',
    })


@login_required
def minhas_reservas(request):
    reservas = (
        Reserva.objects
        .filter(usuario=request.user)
        .select_related('expedicao')
        .prefetch_related('pagamentos', 'fichas_medicas')
        .order_by('-data_reserva')
    )
    return render(request, 'minhas_reservas.html', {'reservas': reservas})


@require_POST
@login_required
def cancelar_reserva(request, reserva_id):
    try:
        services.cancelar_reserva(request.user, reserva_id)
    except DomainError as exc:
        return _domain_error(exc)
    except Exception:
        logger.exception('Erro inesperado no cancelamento')
        return JsonResponse({'success': False, 'message': 'Erro interno.'}, status=500)
    return JsonResponse({
        'success': True,
        'message': 'Reserva cancelada com sucesso. O estorno (se aplicável) foi processado.',
    })


@require_POST
@login_required
def salvar_ficha_medica(request, reserva_id):
    form = FichaMedicaForm(_payload(request))
    if not form.is_valid():
        return JsonResponse({'success': False, 'message': _form_error(form)}, status=400)
    try:
        services.salvar_ficha_medica(request.user, reserva_id, form.cleaned_data)
    except DomainError as exc:
        return _domain_error(exc)
    except Exception:
        logger.exception('Erro inesperado ao salvar ficha médica')
        return JsonResponse({'success': False, 'message': 'Erro interno.'}, status=500)
    return JsonResponse({
        'success': True,
        'message': 'Ficha médica salva com sucesso! Sua expedição está 100% pronta.',
    })


# ─────────────────────────────  Webhook  ─────────────────────────────

@csrf_exempt
@require_POST
def webhook_pagamento(request):
    """Webhook do gateway: valida assinatura HMAC quando PAYMENT_WEBHOOK_SECRET está setado."""
    secret = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', '')
    if not secret:
        # Falha segura: sem segredo configurado não há como autenticar o gateway.
        # Em produção isso é um erro de configuração; em DEBUG permite testes locais.
        if not settings.DEBUG:
            logger.error('PAYMENT_WEBHOOK_SECRET não configurado — webhook rejeitado.')
            return JsonResponse({'success': False, 'message': 'Configuração inválida.'}, status=503)
        logger.warning('Webhook sem validação de assinatura (DEBUG).')
    else:
        signature = request.headers.get('X-Signature', '')
        if not services.verificar_assinatura_webhook(request.body, signature, secret):
            logger.warning('Webhook com assinatura inválida.')
            return JsonResponse({'success': False, 'message': 'Assinatura inválida.'}, status=401)

    try:
        data = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Payload inválido'}, status=400)

    gateway_id = data.get('gateway_id')
    novo_status = data.get('status')
    if not gateway_id:
        return JsonResponse({'success': False, 'message': 'Payload inválido'}, status=400)

    try:
        services.processar_webhook_pagamento(gateway_id, novo_status)
    except DomainError as exc:
        return _domain_error(exc)
    except Exception:
        logger.exception('Erro inesperado no webhook')
        return JsonResponse({'success': False, 'message': 'Erro interno.'}, status=500)
    return JsonResponse({'success': True})
