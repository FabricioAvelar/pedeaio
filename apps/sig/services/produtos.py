from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from apps.pedidos.models import ItemPedido

RECEITA = ExpressionWrapper(
    F('quantidade') * F('preco_unitario'),
    output_field=DecimalField(max_digits=12, decimal_places=2),
)


def _itens_validos():
    return ItemPedido.objects.exclude(pedido__status='Cancelado')


def mais_vendidos(limite=5):
    return (
        _itens_validos()
        .values('produto__nome')
        .annotate(qtd=Sum('quantidade'), receita=Sum(RECEITA))
        .order_by('-qtd')[:limite]
    )


def vendas_por_categoria():
    return (
        _itens_validos()
        .values('produto__categoria__nome')
        .annotate(qtd=Sum('quantidade'), receita=Sum(RECEITA))
        .order_by('-receita')
    )