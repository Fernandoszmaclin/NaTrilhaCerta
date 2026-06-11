"""Testes do app core."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Expedicao, Pagamento, Reserva
from core.services import (
    DomainError,
    cancelar_reserva,
    entrar_lista_espera,
    iniciar_checkout,
    processar_webhook_pagamento,
    verificar_assinatura_webhook,
)


def _make_expedicao(**overrides):
    defaults = dict(
        titulo='Serra Test',
        descricao='Curta',
        data_inicio=date.today() + timedelta(days=10),
        data_fim=date.today() + timedelta(days=12),
        preco=Decimal('500.00'),
        vagas_totais=5,
        ativa=True,
    )
    defaults.update(overrides)
    return Expedicao.objects.create(**defaults)


class ExpedicaoModelTests(TestCase):
    def test_vagas_disponiveis_desconta_reservas_ativas(self):
        exp = _make_expedicao(vagas_totais=10)
        user = User.objects.create_user('u1', password='x')
        Reserva.objects.create(usuario=user, expedicao=exp, quantidade_pessoas=3, status='confirmada')
        self.assertEqual(exp.vagas_disponiveis, 7)

    def test_vagas_disponiveis_ignora_canceladas_e_lista_espera(self):
        exp = _make_expedicao(vagas_totais=10)
        user = User.objects.create_user('u2', password='x')
        Reserva.objects.create(usuario=user, expedicao=exp, quantidade_pessoas=3, status='cancelada')
        Reserva.objects.create(usuario=user, expedicao=exp, quantidade_pessoas=2, status='lista_espera')
        self.assertEqual(exp.vagas_disponiveis, 10)

    def test_duracao_dias(self):
        exp = _make_expedicao()
        self.assertEqual(exp.duracao_dias, 2)


class ReservaSaveTests(TestCase):
    def test_save_calcula_valor_total(self):
        exp = _make_expedicao(preco=Decimal('100.00'))
        user = User.objects.create_user('u3', password='x')
        r = Reserva.objects.create(usuario=user, expedicao=exp, quantidade_pessoas=4)
        self.assertEqual(r.valor_unitario, Decimal('100.00'))
        self.assertEqual(r.valor_total, Decimal('400.00'))


class CheckoutServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('cli', password='x')
        self.exp = _make_expedicao(vagas_totais=2, preco=Decimal('300.00'))

    def test_iniciar_checkout_cria_pagamento(self):
        pag = iniciar_checkout(self.user, self.exp.id, 1)
        self.assertEqual(pag.status, 'pendente')
        self.assertEqual(pag.valor_total, Decimal('300.00'))
        self.assertEqual(Reserva.objects.filter(usuario=self.user).count(), 1)

    def test_iniciar_checkout_sem_vagas(self):
        iniciar_checkout(self.user, self.exp.id, 2)
        with self.assertRaises(DomainError):
            iniciar_checkout(self.user, self.exp.id, 1)

    def test_entrar_lista_espera_unica(self):
        entrar_lista_espera(self.user, self.exp.id)
        with self.assertRaises(DomainError):
            entrar_lista_espera(self.user, self.exp.id)

    def test_cancelar_reserva_estorna_pagamento_aprovado(self):
        pag = iniciar_checkout(self.user, self.exp.id, 1)
        pag.status = 'aprovado'
        pag.save()
        reserva = cancelar_reserva(self.user, pag.reserva.id)
        pag.refresh_from_db()
        self.assertEqual(reserva.status, 'cancelada')
        self.assertEqual(pag.status, 'estornado')


class WebhookTests(TestCase):
    def test_assinatura_invalida_rejeita(self):
        self.assertFalse(verificar_assinatura_webhook(b'{}', 'bad', 'secret'))

    def test_assinatura_valida_aceita(self):
        import hashlib
        import hmac
        body = b'{"x":1}'
        sig = hmac.new(b'secret', body, hashlib.sha256).hexdigest()
        self.assertTrue(verificar_assinatura_webhook(body, sig, 'secret'))

    def test_processar_webhook_aprova(self):
        user = User.objects.create_user('w1', password='x')
        exp = _make_expedicao()
        pag = iniciar_checkout(user, exp.id, 1)
        processar_webhook_pagamento(pag.gateway_id, 'approved')
        pag.refresh_from_db()
        self.assertEqual(pag.status, 'aprovado')
        self.assertEqual(pag.reserva.status, 'confirmada')

    def test_processar_webhook_idempotente(self):
        user = User.objects.create_user('w2', password='x')
        exp = _make_expedicao()
        pag = iniciar_checkout(user, exp.id, 1)
        processar_webhook_pagamento(pag.gateway_id, 'approved')
        # 2ª chamada não deve estourar nem alterar
        processar_webhook_pagamento(pag.gateway_id, 'rejected')
        pag.refresh_from_db()
        self.assertEqual(pag.status, 'aprovado')


class ViewAuthTests(TestCase):
    def test_signup_e_login_via_json(self):
        c = Client()
        resp = c.post(reverse('signup'),
                      data='{"first_name":"João","last_name":"S","email":"j@ex.com","username":"joao","password":"Expedicao#2024","password2":"Expedicao#2024"}',
                      content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])

    def test_signup_senha_curta(self):
        c = Client()
        resp = c.post(reverse('signup'),
                      data='{"first_name":"A","email":"a@a.com","username":"a","password":"1","password2":"1"}',
                      content_type='application/json')
        self.assertEqual(resp.status_code, 400)

    def test_login_admin_bloqueado(self):
        User.objects.create_superuser('admin1', 'a@a.com', 'adm12345')
        c = Client()
        resp = c.post(reverse('login'),
                      data='{"username":"admin1","password":"adm12345"}',
                      content_type='application/json')
        self.assertEqual(resp.status_code, 400)
