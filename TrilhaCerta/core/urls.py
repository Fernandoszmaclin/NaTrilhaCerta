from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expedicoes/', views.expedicoes_lista, name='expedicoes'),
    path('contato/', views.contato, name='contato'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('api/v1/pagamentos/checkout/', views.checkout_view, name='checkout'),
    path('api/v1/pagamentos/webhook/', views.webhook_pagamento, name='webhook_pagamento'),
    path('api/v1/lista-espera/', views.entrar_lista_espera, name='lista_espera'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('api/v1/reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('api/v1/reservas/<int:reserva_id>/ficha-medica/', views.salvar_ficha_medica, name='salvar_ficha_medica'),
]