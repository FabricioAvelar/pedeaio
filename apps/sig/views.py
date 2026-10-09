from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .services import vendas, produtos, clientes, entregas


def _serie(linhas, rotulo, valor):
    return {
        'labels': [str(l[rotulo]) for l in linhas],
        'valores': [float(l[valor] or 0) for l in linhas],
    }


@staff_member_required(login_url='login')
def dashboard(request):
    mes = [
        {'rotulo': l['mes'].strftime('%m/%Y'), 'total': l['total']}
        for l in vendas.faturamento_por_mes()
    ]

    pagamento = entregas.receita_por_forma_pagamento()
    tempo = entregas.tempo_medio('Saiu para entrega', 'Entregue')

    graficos = {
        'mes': _serie(mes, 'rotulo', 'total'),
        'produtos': _serie(produtos.mais_vendidos(), 'produto__nome', 'qtd'),
        'categorias': _serie(produtos.vendas_por_categoria(), 'produto__categoria__nome', 'receita'),
        'status': _serie(entregas.pedidos_por_status(), 'status', 'qtd'),
        'pagamento': _serie(pagamento, 'forma_pagamento', 'total'),   # NOVO
    }

    context = {
        'resumo': vendas.resumo_geral(),
        'total_clientes': clientes.total_clientes(),
        'taxa_media': entregas.taxa_media(),
        'top_clientes': clientes.clientes_que_mais_compram(),
        'por_cidade': entregas.pedidos_por_cidade(),
        'graficos': graficos,
        # NOVOS
        'tempo_entrega_min': round(tempo.total_seconds() / 60) if tempo else None,
        'por_entregador': entregas.entregas_por_entregador(),
    }
    return render(request, 'privado/sig_dashboard.html', context)