from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expedicoes/', views.expedicoes_lista, name='expedicoes'),
    path('contato/', views.contato, name='contato'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]