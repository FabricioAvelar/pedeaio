from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST

from apps.pedidos.models import Pedido, HistoricoStatus


def entregador_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_entregador:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

@entregador_required
def painel_entregador(request):
    disponiveis = Pedido.objects.filter(
        status='Pronto para entrega', entregador__isnull=True
    ).select_related('endereco').prefetch_related(
        'itens__produto'
    ).order_by('criado_em')

    minhas = Pedido.objects.filter(
        entregador=request.user, status='Saiu para entrega'
    ).select_related('endereco', 'usuario').prefetch_related('itens__produto')

    return render(request, 'privado/painel_entregador.html',
                  {'disponiveis': disponiveis, 'minhas': minhas})

@entregador_required
@require_POST
def aceitar_entrega(request, pedido_id):
    # update() com filtro é atômico: se dois entregadores clicarem juntos,
    # só um consegue (o outro recebe 0 linhas atualizadas).
    with transaction.atomic():
        atualizados = Pedido.objects.filter(
            id=pedido_id,
            status='Pronto para entrega',
            entregador__isnull=True,
        ).update(entregador=request.user, status='Saiu para entrega')

        if atualizados:
            HistoricoStatus.objects.create(
                pedido_id=pedido_id,
                status='Saiu para entrega',
                alterado_por=request.user,
            )

    if atualizados:
        messages.success(request, 'Entrega aceita. Boa viagem!')
    else:
        messages.error(request, 'Esse pedido não está mais disponível.')

    return redirect('painel_entregador')


@entregador_required
@require_POST
def concluir_entrega(request, pedido_id):
    pedido = get_object_or_404(
        Pedido, id=pedido_id,
        entregador=request.user, status='Saiu para entrega'
    )

    with transaction.atomic():
        pedido.mudar_status('Entregue', request.user)
        if not pedido.pago:
            pedido.marcar_como_pago()   # cartão/dinheiro: recebido na entrega

    messages.success(request, f'Pedido #{pedido.id} entregue!')
    return redirect('painel_entregador')