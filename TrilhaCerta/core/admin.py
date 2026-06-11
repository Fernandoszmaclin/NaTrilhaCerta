from django.contrib import admin
from .models import Expedicao, Reserva, ImagemExpedicao, Pagamento, FichaMedica

class ImagemExpedicaoInline(admin.TabularInline):
    model = ImagemExpedicao
    extra = 1

@admin.register(Expedicao)
class ExpedicaoAdmin(admin.ModelAdmin):
    """
    Configuração do painel Admin para gerenciar pacotes de viagem.
    Permite adicionar, editar e remover expedições diretamente.
    """
    list_display = ('titulo', 'destino', 'data_inicio', 'data_fim', 'preco', 'vagas_totais', 'dificuldade', 'ativa')
    list_filter = ('ativa', 'dificuldade', 'data_inicio')
    search_fields = ('titulo', 'destino', 'descricao')
    list_editable = ('ativa', 'vagas_totais', 'preco')
    date_hierarchy = 'data_inicio'
    ordering = ('data_inicio',)
    inlines = [ImagemExpedicaoInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'destino', 'descricao', 'descricao_completa', 'dificuldade')
        }),
        ('Datas e Disponibilidade', {
            'fields': ('data_inicio', 'data_fim', 'vagas_totais', 'ativa')
        }),
        ('Preço', {
            'fields': ('preco',)
        }),
    )

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Configuração do painel Admin para gerenciar reservas de usuários.
    Permite visualizar, filtrar e alterar o status das reservas.
    """
    list_display = ('usuario', 'expedicao', 'status', 'quantidade_pessoas', 'valor_total', 'data_reserva')
    list_filter = ('status', 'expedicao', 'data_reserva')
    search_fields = ('usuario__username', 'usuario__first_name', 'expedicao__titulo')
    list_editable = ('status',)
    readonly_fields = ('data_reserva',)
    ordering = ('-data_reserva',)

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    """Admin para gerenciar e visualizar pagamentos do sistema."""
    list_display = ('id', 'reserva', 'metodo_pagamento', 'valor_total', 'status', 'criado_em')
    list_filter = ('status', 'metodo_pagamento', 'criado_em')
    search_fields = ('id', 'reserva__usuario__username', 'reserva__expedicao__titulo', 'gateway_id')
    readonly_fields = ('id', 'criado_em', 'atualizado_em')
    list_editable = ('status',)

@admin.register(FichaMedica)
class FichaMedicaAdmin(admin.ModelAdmin):
    """Admin para gerenciar fichas médicas de passageiros."""
    list_display = ('nome_completo', 'reserva', 'tipo_sanguineo', 'contato_emergencia')
    search_fields = ('nome_completo', 'reserva__usuario__username', 'contato_emergencia', 'restricoes_alimentares')
