from django.db import models

# Create your models here.

class Expedicao(models.Model):
    """
    Modelo que representa uma viagem/expedição no banco de dados.
    """
    titulo = models.CharField(max_length=150, verbose_name="Título")
    descricao = models.CharField(max_length=255, verbose_name="Descrição Curta")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Término")
    duracao_dias = models.IntegerField(verbose_name="Duração em Dias")
    imagem = models.ImageField(upload_to='expedicoes/', verbose_name="Imagem de Destaque")
    ativa = models.BooleanField(default=True, verbose_name="Reserva Aberta?")

    # Esta função faz com que o nome da expedição apareça bonito no painel Admin
    def __str__(self):
        return self.titulo