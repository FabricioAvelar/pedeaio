from django.db.models import Count, Avg
from apps.pedidos.models import Pedido


def pedidos_por_status():
    return Pedido.objects.values('status').annotate(qtd=Count('id')).order_by('-qtd')


def pedidos_por_cidade():
    return (
        Pedido.objects.exclude(status='Cancelado')
        .values('endereco__cidade', 'endereco__estado')
        .annotate(qtd=Count('id'))
        .order_by('-qtd')
    )


def taxa_media():
    return Pedido.objects.aggregate(media=Avg('taxa_entrega'))['media']