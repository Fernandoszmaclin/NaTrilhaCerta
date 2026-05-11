from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

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
    data_inicio = models.DateField(verbose_name="Data de Saída")
    data_fim = models.DateField(verbose_name="Data de Volta")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Atual (R$)", default=0)
    destino = models.CharField(max_length=200, verbose_name="Destino / Local", blank=True)
    dificuldade = models.CharField(max_length=20, choices=DIFICULDADE_CHOICES, default='moderado', verbose_name="Nível de Dificuldade")
    vagas_totais = models.IntegerField(verbose_name="Vagas Totais", default=20)
    ativa = models.BooleanField(default=True, verbose_name="Reserva Aberta?")
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
        """Calcula vagas subtraindo as reservas não canceladas."""
        reservas_ativas = self.reservas.exclude(status='cancelada').aggregate(
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

    @property
    def imagem(self):
        primeira = self.imagens.first()
        return primeira.imagem if primeira else None

    @property
    def imagem_2(self):
        imgs = self.imagens.all()
        return imgs[1].imagem if imgs.count() > 1 else None

    @property
    def imagem_3(self):
        imgs = self.imagens.all()
        return imgs[2].imagem if imgs.count() > 2 else None


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
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas', verbose_name="Usuário")
    expedicao = models.ForeignKey(Expedicao, on_delete=models.PROTECT, related_name='reservas', verbose_name="Expedição")
    data_reserva = models.DateTimeField(auto_now_add=True, verbose_name="Data da Reserva")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    quantidade_pessoas = models.PositiveIntegerField(default=1, verbose_name="Quantidade de Pessoas")
    
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário Pago (R$)", default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total (R$)", default=0.00)
    
    observacoes = models.TextField(blank=True, verbose_name="Observações", help_text="Informações adicionais ou pedidos especiais")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-data_reserva']

    def save(self, *args, **kwargs):
        # Auto-preenche os valores financeiros baseados no preço atual na hora da reserva
        if not self.pk and (not self.valor_unitario or self.valor_unitario == 0):
            self.valor_unitario = self.expedicao.preco
            self.valor_total = self.valor_unitario * self.quantidade_pessoas
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} → {self.expedicao.titulo}"