from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from apps.pedidos.models import Pedido


def pedidos_validos():
    return Pedido.objects.exclude(status='Cancelado')


def resumo_geral():
    return pedidos_validos().aggregate(
        faturamento=Sum('valor_total'),
        qtd_pedidos=Count('id'),
        ticket_medio=Avg('valor_total'),
        total_taxas=Sum('taxa_entrega'),
    )


def faturamento_por_mes():
    return (
        pedidos_validos()
        .annotate(mes=TruncMonth('criado_em'))
        .values('mes')
        .annotate(total=Sum('valor_total'), qtd=Count('id'))
        .order_by('mes')
    )