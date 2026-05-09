from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Expedicao


def home(request):
    """Home com expedições em destaque."""
    from django.utils import timezone
    hoje = timezone.now().date()
    expedicoes = Expedicao.objects.filter(ativa=True, data_inicio__gte=hoje).order_by('data_inicio')[:6]
    context = {
        'expedicoes': expedicoes
    }
    return render(request, 'index.html', context)


def expedicoes_lista(request):
    """Lista todas as expedições."""
    from django.utils import timezone
    hoje = timezone.now().date()
    expedicoes = Expedicao.objects.filter(ativa=True, data_inicio__gte=hoje).order_by('data_inicio')
    context = {
        'expedicoes': expedicoes
    }
    return render(request, 'expedicoes.html', context)


def contato(request):
    """Página de contato."""
    return render(request, 'contato.html')


@require_POST
def login_view(request):
    """Login via AJAX."""
    try:
        data = json.loads(request.body)
        username = data.get('username', '')
        password = data.get('password', '')
    except json.JSONDecodeError:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        # Bloqueia admin no modal por segurança.
        if user.is_staff or user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'Usuário ou senha incorretos.'
            }, status=400)

        login(request, user)
        return JsonResponse({
            'success': True,
            'message': f'Bem-vindo de volta, {user.first_name or user.username}!',
            'username': user.first_name or user.username
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Usuário ou senha incorretos.'
        }, status=400)


@require_POST
def signup_view(request):
    """Cadastro via AJAX."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    password2 = data.get('password2', '')


    if not all([first_name, username, email, password, password2]):
        return JsonResponse({'success': False, 'message': 'Todos os campos obrigatórios devem ser preenchidos.'}, status=400)

    if password != password2:
        return JsonResponse({'success': False, 'message': 'As senhas não coincidem.'}, status=400)

    if len(password) < 6:
        return JsonResponse({'success': False, 'message': 'A senha deve ter pelo menos 6 caracteres.'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'success': False, 'message': 'Este nome de usuário já está em uso.'}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'Este e-mail já está cadastrado.'}, status=400)


    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    login(request, user)
    return JsonResponse({
        'success': True,
        'message': f'Conta criada com sucesso! Bem-vindo, {first_name}!',
        'username': first_name
    })


def logout_view(request):
    """Logout e redirecionamento."""
    logout(request)
    return redirect('home')