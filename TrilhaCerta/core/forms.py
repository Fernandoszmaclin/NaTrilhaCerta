"""Formulários do app core — validação centralizada (substitui validação manual nas views)."""

from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(max_length=128)


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    password = forms.CharField(min_length=8, max_length=128)
    password2 = forms.CharField(min_length=8, max_length=128)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned


class CheckoutForm(forms.Form):
    expedicao_id = forms.IntegerField(min_value=1)
    quantidade_pessoas = forms.IntegerField(min_value=1, max_value=20)


class ListaEsperaForm(forms.Form):
    expedicao_id = forms.IntegerField(min_value=1)


class FichaMedicaForm(forms.Form):
    nome_completo = forms.CharField(max_length=150, required=False)
    restricoes_alimentares = forms.CharField(required=False)
    tipo_sanguineo = forms.CharField(max_length=5, required=False)
    contato_emergencia = forms.CharField(max_length=255)
