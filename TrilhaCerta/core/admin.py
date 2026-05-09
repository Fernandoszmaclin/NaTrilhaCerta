from django.contrib import admin
from .models import Expedicao, Reserva



@admin.register(Expedicao)
class ExpedicaoAdmin(admin.ModelAdmin):
    """
    Configuração do painel Admin para gerenciar pacotes de viagem.
    Permite adicionar, editar e remover expedições diretamente.
    """
    list_display = ('titulo', 'destino', 'data_inicio', 'data_fim', 'preco', 'vagas', 'dificuldade', 'ativa')
    list_filter = ('ativa', 'dificuldade', 'data_inicio')
    search_fields = ('titulo', 'destino', 'descricao')
    list_editable = ('ativa', 'vagas', 'preco')
    date_hierarchy = 'data_inicio'
    ordering = ('data_inicio',)

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'destino', 'descricao', 'descricao_completa', 'dificuldade')
        }),
        ('Datas e Disponibilidade', {
            'fields': ('data_inicio', 'data_fim', 'duracao_dias', 'vagas', 'ativa')
        }),
        ('Preço', {
            'fields': ('preco',)
        }),
        ('Imagens', {
            'fields': ('imagem', 'imagem_2', 'imagem_3'),
            'description': 'A imagem principal é obrigatória. As demais são opcionais.'
        }),
    )


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Configuração do painel Admin para gerenciar reservas de usuários.
    Permite visualizar, filtrar e alterar o status das reservas.
    """
    list_display = ('usuario', 'expedicao', 'status', 'quantidade_pessoas', 'data_reserva')
    list_filter = ('status', 'expedicao', 'data_reserva')
    search_fields = ('usuario__username', 'usuario__first_name', 'expedicao__titulo')
    list_editable = ('status',)
    readonly_fields = ('data_reserva',)
    ordering = ('-data_reserva',)
