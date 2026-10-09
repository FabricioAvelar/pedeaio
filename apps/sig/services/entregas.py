from django.db.models import (
    Count, Avg, Sum, F, OuterRef, Subquery, ExpressionWrapper, DurationField
)
from apps.pedidos.models import Pedido, HistoricoStatus


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


# ---------- NOVOS ----------

def _momento(status):
    """Primeiro horário em que o pedido chegou nesse status."""
    return Subquery(
        HistoricoStatus.objects.filter(pedido=OuterRef('pk'), status=status)
        .order_by('criado_em').values('criado_em')[:1]
    )


def tempo_medio(de_status, ate_status):
    """Tempo médio (timedelta) entre dois status; None se não houver dados."""
    qs = (
        Pedido.objects.filter(status='Entregue')
        .annotate(inicio=_momento(de_status), fim=_momento(ate_status))
        .annotate(duracao=ExpressionWrapper(
            F('fim') - F('inicio'), output_field=DurationField()
        ))
    )
    return qs.aggregate(media=Avg('duracao'))['media']


def receita_por_forma_pagamento():
    return (
        Pedido.objects.exclude(status='Cancelado').exclude(forma_pagamento='')
        .values('forma_pagamento')
        .annotate(qtd=Count('id'), total=Sum('valor_total'))
        .order_by('-total')
    )


def entregas_por_entregador():
    return (
        Pedido.objects.filter(status='Entregue', entregador__isnull=False)
        .values('entregador__first_name', 'entregador__email')
        .annotate(qtd=Count('id'))
        .order_by('-qtd')
    )