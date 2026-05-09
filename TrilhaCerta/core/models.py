from django.db import models
from django.contrib.auth.models import User



class Expedicao(models.Model):
    """Modelo de expedição para gestão de viagens."""
    titulo = models.CharField(max_length=150, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição Curta", help_text="Breve descrição da expedição (exibida nos cards)")
    descricao_completa = models.TextField(verbose_name="Descrição Completa", blank=True, help_text="Descrição detalhada da expedição")
    data_inicio = models.DateField(verbose_name="Data de Saída")
    data_fim = models.DateField(verbose_name="Data de Volta")
    duracao_dias = models.IntegerField(verbose_name="Duração em Dias")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço (R$)", default=0)
    imagem = models.ImageField(upload_to='expedicoes/', verbose_name="Imagem Principal")
    imagem_2 = models.ImageField(upload_to='expedicoes/', verbose_name="Imagem 2", blank=True, null=True)
    imagem_3 = models.ImageField(upload_to='expedicoes/', verbose_name="Imagem 3", blank=True, null=True)
    destino = models.CharField(max_length=200, verbose_name="Destino / Local", blank=True)
    dificuldade = models.CharField(
        max_length=20,
        choices=[
            ('facil', 'Fácil'),
            ('moderado', 'Moderado'),
            ('dificil', 'Difícil'),
            ('extremo', 'Extremo'),
        ],
        default='moderado',
        verbose_name="Nível de Dificuldade"
    )
    vagas = models.IntegerField(verbose_name="Vagas Disponíveis", default=20)
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
    def esgotada(self):
        return self.vagas <= 0


class Reserva(models.Model):
    """Vincula usuário a uma expedição."""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name="Usuário"
    )
    expedicao = models.ForeignKey(
        Expedicao,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name="Expedição"
    )
    data_reserva = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Reserva"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    quantidade_pessoas = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade de Pessoas"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Informações adicionais ou pedidos especiais"
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-data_reserva']
        # Evita reservas duplicadas do mesmo usuário
        unique_together = ['usuario', 'expedicao']

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} → {self.expedicao.titulo}"