from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from apps.usuarios.models import Usuario
from apps.pedidos.models import Pedido


def total_clientes():
    return Usuario.objects.filter(is_staff=False).count()


def novos_por_mes():
    return (
        Usuario.objects.filter(is_staff=False)
        .annotate(mes=TruncMonth('date_joined'))
        .values('mes')
        .annotate(qtd=Count('cpf'))
        .order_by('mes')
    )


def clientes_que_mais_compram(limite=5):
    return (
        Pedido.objects.exclude(status='Cancelado')
        .values('usuario__username')
        .annotate(qtd=Count('id'), total=Sum('valor_total'))
        .order_by('-total')[:limite]
    )