from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .services import vendas, produtos, clientes, entregas


def _serie(linhas, rotulo, valor):
    return {
        'labels': [str(l[rotulo]) for l in linhas],
        'valores': [float(l[valor] or 0) for l in linhas],
    }


@staff_member_required
def dashboard(request):
    mes = [
        {'rotulo': l['mes'].strftime('%m/%Y'), 'total': l['total']}
        for l in vendas.faturamento_por_mes()
    ]

    graficos = {
        'mes': _serie(mes, 'rotulo', 'total'),
        'produtos': _serie(produtos.mais_vendidos(), 'produto__nome', 'qtd'),
        'categorias': _serie(produtos.vendas_por_categoria(), 'produto__categoria__nome', 'receita'),
        'status': _serie(entregas.pedidos_por_status(), 'status', 'qtd'),
    }

    context = {
        'resumo': vendas.resumo_geral(),
        'total_clientes': clientes.total_clientes(),
        'taxa_media': entregas.taxa_media(),
        'top_clientes': clientes.clientes_que_mais_compram(),
        'por_cidade': entregas.pedidos_por_cidade(),
        'graficos': graficos,
    }
    return render(request, 'privado/sig_dashboard.html', context)