from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.pedidos.models import Pedido

# O admin só mexe nessas etapas. "Saiu" e "Entregue" são do entregador.
STATUS_ADMIN = ['Preparando', 'Pronto para entrega', 'Cancelado']


@staff_member_required(login_url='login')
def pedidos_lista(request):
    status = request.GET.get('status', '')

    pedidos = Pedido.objects.select_related(
        'usuario', 'entregador'
    ).order_by('-criado_em')

    if status in dict(Pedido.STATUS_CHOICES):
        pedidos = pedidos.filter(status=status)

    return render(request, 'privado/painel_pedidos.html', {
        'pedidos': pedidos,
        'status_atual': status,
        'status_choices': Pedido.STATUS_CHOICES,
    })


@staff_member_required(login_url='login')
def pedido_gerenciar(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.select_related('usuario', 'endereco', 'entregador'),
        id=pedido_id
    )
    proximos = [
        s for s in Pedido.TRANSICOES[pedido.status] if s in STATUS_ADMIN
    ]
    return render(request, 'privado/painel_pedido.html',
                  {'pedido': pedido, 'proximos': proximos})


@staff_member_required(login_url='login')
@require_POST
def alterar_status(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    novo = request.POST.get('status')

    if novo not in STATUS_ADMIN:
        messages.error(request, 'Status inválido.')
        return redirect('painel_pedido', pedido_id=pedido.id)

    if novo == 'Preparando':
        if not pedido.forma_pagamento:
            messages.error(
                request, 'O cliente ainda não escolheu a forma de pagamento.'
            )
            return redirect('painel_pedido', pedido_id=pedido.id)

        if pedido.forma_pagamento == 'Pix' and not pedido.pago:
            messages.error(
                request, 'Confirme o recebimento do Pix antes de preparar.'
            )
            return redirect('painel_pedido', pedido_id=pedido.id)

    try:
        pedido.mudar_status(novo, request.user)
        messages.success(request, f'Pedido #{pedido.id} agora está: {novo}.')
    except ValueError as erro:
        messages.error(request, str(erro))

    return redirect('painel_pedido', pedido_id=pedido.id)


@staff_member_required(login_url='login')
@require_POST
def confirmar_pagamento(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, forma_pagamento='Pix')
    pedido.marcar_como_pago()
    messages.success(request, 'Pagamento confirmado.')
    return redirect('painel_pedido', pedido_id=pedido.id)