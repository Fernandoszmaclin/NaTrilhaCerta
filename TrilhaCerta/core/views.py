from django.shortcuts import render
from .models import Expedicao

def home(request):
    # Busca expedições ativas ordenadas por data mais próxima
    expedicoes = Expedicao.objects.filter(ativa=True).order_by('data_inicio')[:6]
    
    context = {
        'expedicoes': expedicoes
    }
    return render(request, 'index.html', context)