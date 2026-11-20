from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .services import cardapio, clientes, demanda, entregas


@staff_member_required(login_url='login')
def dashboard(request):
    analise_cardapio = cardapio.analise()
    analise_demanda = demanda.analise()
    analise_clientes = clientes.analise()
    etapas, gargalo = entregas.gargalos()

    graficos = {
        'hora': {
            'labels': [f'{h:02d}h' for h in range(24)],
            'valores': analise_demanda['por_hora'],
        },
    }

    context = {
        'periodo_dias': cardapio.PERIODO_DIAS,
        'cardapio': analise_cardapio,
        'demanda': analise_demanda,
        'etapas': etapas,
        'gargalo': gargalo,
        'cancelamento': entregas.cancelamento(),
        'clientes': analise_clientes,
        'graficos': graficos,
    }
    return render(request, 'privado/sad_dashboard.html', context)