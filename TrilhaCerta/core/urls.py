from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('expedicoes/', views.expedicoes_view, name='expedicoes'),
    path('contato/', views.contato_view, name='contato'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('api/v1/pagamentos/checkout/', views.checkout_view, name='checkout'),
    path('api/v1/pagamentos/webhook/', views.webhook_pagamento_view, name='webhook_pagamento'),
    path('api/v1/lista-espera/', views.lista_espera_view, name='lista_espera'),
    path('minhas-reservas/', views.minhas_reservas_view, name='minhas_reservas'),
    path('api/v1/reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva_view, name='cancelar_reserva'),
    path('api/v1/reservas/<int:reserva_id>/ficha-medica/', views.salvar_ficha_medica_view, name='salvar_ficha_medica'),
]