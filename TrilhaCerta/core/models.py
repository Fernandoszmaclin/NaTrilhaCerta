from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
import uuid

class Expedicao(models.Model):
    """Modelo de expedição para gestão de viagens."""
    DIFICULDADE_CHOICES = [
        ('facil', 'Fácil'),
        ('moderado', 'Moderado'),
        ('dificil', 'Difícil'),
        ('extremo', 'Extremo'),
    ]

    titulo = models.CharField(max_length=150, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição Curta", help_text="Breve descrição da expedição (exibida nos cards)")
    descricao_completa = models.TextField(verbose_name="Descrição Completa", blank=True, help_text="Descrição detalhada da expedição")
    data_inicio = models.DateField(verbose_name="Data de Saída", db_index=True)
    data_fim = models.DateField(verbose_name="Data de Volta")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Atual (R$)", default=0)
    destino = models.CharField(max_length=200, verbose_name="Destino / Local", blank=True)
    dificuldade = models.CharField(max_length=20, choices=DIFICULDADE_CHOICES, default='moderado', verbose_name="Nível de Dificuldade")
    vagas_totais = models.IntegerField(verbose_name="Vagas Totais", default=20)
    ativa = models.BooleanField(default=True, verbose_name="Reserva Aberta?", db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Expedição"
        verbose_name_plural = "Expedições"
        ordering = ['data_inicio']

    def __str__(self):
        return self.titulo

    @property
    def duracao_dias(self):
        """Calcula dinamicamente a duração, evitando redundância no banco."""
        if self.data_fim and self.data_inicio:
            return (self.data_fim - self.data_inicio).days
        return 0

    @property
    def vagas_disponiveis(self):
        """Calcula vagas subtraindo as reservas confirmadas ou pendentes (ignora lista de espera)."""
        reservas_ativas = self.reservas.exclude(status__in=['cancelada', 'lista_espera']).aggregate(
            total=models.Sum('quantidade_pessoas')
        )['total'] or 0
        return self.vagas_totais - reservas_ativas

    @property
    def esgotada(self):
        return self.vagas_disponiveis <= 0

    # PROPRIEDADES DE COMPATIBILIDADE COM O TEMPLATE ANTIGO
    @property
    def vagas(self):
        return self.vagas_disponiveis

    def _imagem_na_posicao(self, indice):
        """Retorna a imagem na posição dada (0-based) ou None.

        Materializa o queryset uma vez para reaproveitar o prefetch_related
        e evitar uma query extra de .count() por acesso.
        """
        imgs = list(self.imagens.all())
        return imgs[indice].imagem if len(imgs) > indice else None

    @property
    def imagem(self):
        return self._imagem_na_posicao(0)

    @property
    def imagem_2(self):
        return self._imagem_na_posicao(1)

    @property
    def imagem_3(self):
        return self._imagem_na_posicao(2)


class ImagemExpedicao(models.Model):
    """Nova entidade para armazenar múltiplas imagens por expedição."""
    expedicao = models.ForeignKey(Expedicao, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='expedicoes/')
    is_principal = models.BooleanField(default=False, verbose_name="Imagem Principal")
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_principal', 'ordem']
        verbose_name = "Imagem da Expedição"
        verbose_name_plural = "Imagens da Expedição"


class Reserva(models.Model):
    """Vincula usuário a uma expedição com integridade financeira."""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('confirmada_e_pronta', 'Confirmada e Pronta'),
        ('lista_espera', 'Lista de Espera'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas', verbose_name="Usuário")
    expedicao = models.ForeignKey(Expedicao, on_delete=models.PROTECT, related_name='reservas', verbose_name="Expedição")
    data_reserva = models.DateTimeField(auto_now_add=True, verbose_name="Data da Reserva")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status", db_index=True)
    quantidade_pessoas = models.PositiveIntegerField(default=1, verbose_name="Quantidade de Pessoas")
    
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário Pago (R$)", default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total (R$)", default=0.00)
    
    observacoes = models.TextField(blank=True, verbose_name="Observações", help_text="Informações adicionais ou pedidos especiais")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-data_reserva']

    def save(self, *args, **kwargs):
        # Na criação, deriva os valores financeiros do preço atual da expedição,
        # exceto quando um valor_total foi informado explicitamente (ex.: desconto).
        # Usar valor_total como gatilho preserva expedições gratuitas (preço 0).
        if not self.pk and not self.valor_total:
            self.valor_unitario = self.expedicao.preco
            self.valor_total = self.valor_unitario * self.quantidade_pessoas
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} → {self.expedicao.titulo}"


class Pagamento(models.Model):
    """Armazena o histórico financeiro e transacional (@/database & @/secure)."""
    METODO_CHOICES = [
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
    ]
    STATUS_PAGAMENTO_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('estornado', 'Estornado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagamentos')
    gateway_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID no Gateway", help_text="ID da transação no Mercado Pago/Stripe")
    metodo_pagamento = models.CharField(max_length=50, choices=METODO_CHOICES, verbose_name="Método de Pagamento")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    status = models.CharField(max_length=20, choices=STATUS_PAGAMENTO_CHOICES, default='pendente', db_index=True)
    qr_code_pix = models.TextField(blank=True, null=True, verbose_name="PIX Copia e Cola")
    link_recibo = models.URLField(blank=True, null=True, verbose_name="Link do Recibo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-criado_em']

    def __str__(self):
        return f"Pagamento {self.id} - {self.get_status_display()}"


class FichaMedica(models.Model):
    """Ficha obrigatória para cada participante, garantindo segurança e normalização (1:N com Reserva)."""
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='fichas_medicas')
    nome_completo = models.CharField(max_length=150, verbose_name="Nome Completo do Participante", default="Não informado")
    restricoes_alimentares = models.TextField(blank=True, verbose_name="Restrições Alimentares")
    tipo_sanguineo = models.CharField(max_length=5, blank=True, verbose_name="Tipo Sanguíneo")
    contato_emergencia = models.CharField(max_length=255, verbose_name="Contato de Emergência (Nome e Telefone)")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ficha Médica"
        verbose_name_plural = "Fichas Médicas"

    def __str__(self):
        return f"Ficha de {self.nome_completo} (Reserva: {self.reserva.id})"