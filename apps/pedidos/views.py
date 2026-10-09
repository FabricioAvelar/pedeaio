from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from .pix import gerar_codigo_pix

from apps.usuarios.models import Endereco
from apps.produtos.models import Carrinho, ItemCarrinho
from .models import Pedido, ItemPedido, HistoricoStatus
from .forms import PagamentoForm


@login_required
def finalizar_pedido(request):
    carrinho = get_object_or_404(Carrinho, usuario=request.user)
    itens = ItemCarrinho.objects.filter(carrinho=carrinho)

    if not itens.exists():
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('carrinhocompras')

    enderecos = Endereco.objects.filter(usuario=request.user)

    if not enderecos.exists():
        messages.info(request, 'Cadastre um endereço para continuar.')
        return redirect(reverse('endereco_cadastrar') + '?origem=carrinho')

    taxas_entrega = {
        'Canguaretama': Decimal('5.00'),
        'Barra do Cunhaú': Decimal('7.00'),
        'Goianinha': Decimal('8.00'),
        'Natal': Decimal('15.00'),
    }

    subtotal = sum(item.subtotal for item in itens)

    # taxa de cada endereço, só para exibir no HTML
    for endereco in enderecos:
        endereco.frete = taxas_entrega.get(endereco.cidade)

    if request.method == 'POST':
        endereco_id = request.POST.get('endereco')

        if not endereco_id:
            messages.error(request, 'Selecione um endereço de entrega.')
            return redirect('finalizar_pedido')

        endereco = get_object_or_404(
            Endereco, id=endereco_id, usuario=request.user
        )

        taxa_entrega = taxas_entrega.get(endereco.cidade)

        if taxa_entrega is None:
            messages.error(request, 'Não realizamos entregas para esta cidade.')
            return redirect('finalizar_pedido')

        total = subtotal + taxa_entrega

        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                endereco=endereco,
                taxa_entrega=taxa_entrega,
                valor_total=total,
            )

            for item in itens:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item.produto,
                    quantidade=item.quantidade,
                    preco_unitario=item.produto.preco,
                )

            # NOVO: primeiro registro do acompanhamento
            HistoricoStatus.objects.create(
                pedido=pedido, status='Pendente', alterado_por=request.user
            )

            itens.delete()

        # NOVO: em vez da tela de sucesso, vai escolher o pagamento
        return redirect('pagamento', pedido_id=pedido.id)

    context = {
        'itens': itens,
        'total': subtotal,
        'enderecos': enderecos,
    }
    return render(request, 'privado/finalizar_pedido.html', context)


@login_required
def pagar(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # já escolheu a forma de pagamento
    if pedido.forma_pagamento:
        return redirect('pedido_detalhes', pedido_id=pedido.id)

    form = PagamentoForm(request.POST or None, instance=pedido)

    if request.method == 'POST' and form.is_valid():
        troco = form.cleaned_data['troco_para']

        if troco and troco < pedido.valor_total:
            form.add_error(
                'troco_para',
                'O troco precisa ser maior que o total do pedido.'
            )
        else:
            pedido = form.save(commit=False)
            if pedido.forma_pagamento != 'Dinheiro':
                pedido.troco_para = None
            pedido.save(update_fields=['forma_pagamento', 'troco_para'])
            messages.success(request, 'Forma de pagamento registrada!')
            return redirect('pedido_detalhes', pedido_id=pedido.id)

    return render(request, 'privado/pagamento.html', {
        'pedido': pedido,
        'form': form,
        'codigo_pix': gerar_codigo_pix(pedido),
    })


@login_required
def sucesso(request):
    return render(request, 'privado/sucesso.html')


@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'privado/meus_pedidos.html', {'pedidos': pedidos})


@login_required
def pedido_detalhes(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    subtotal = pedido.valor_total - pedido.taxa_entrega
    return render(request, 'privado/pedido_detalhes.html',
                  {'pedido': pedido, 'subtotal': subtotal})


@login_required
def pedido_status(request, pedido_id):
    """Usada pelo JavaScript da página de acompanhamento."""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return JsonResponse({'status': pedido.status})