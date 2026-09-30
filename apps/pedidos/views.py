from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from django.urls import reverse

# Usuário
from apps.usuarios.models import Endereco
from apps.produtos.models import Carrinho, ItemCarrinho
from .models import Pedido, ItemPedido


@login_required
def finalizar_pedido(request):
    carrinho = get_object_or_404(Carrinho, usuario=request.user)

    itens = ItemCarrinho.objects.filter(
        carrinho=carrinho
    )

    if not itens.exists():
        messages.error(
            request,
            'Seu carrinho está vazio.'
        )

        return redirect('carrinhocompras')

    enderecos = Endereco.objects.filter(usuario=request.user)

    if not enderecos.exists():
        messages.info(
            request,
            'Cadastre um endereço para continuar.'
        )

        return redirect(
            reverse('endereco_cadastrar')
            + '?origem=carrinho'
        )

    if request.method == 'POST':
        endereco_id = request.POST.get('endereco')

        endereco = get_object_or_404(
            Endereco,
            id=endereco_id,
            usuario=request.user
        )

        taxas_entrega = {
            'Canguaretama': Decimal('5.00'),
            'Barra do Cunhaú': Decimal('7.00'),
            'Goianinha': Decimal('8.00'),
            'Natal': Decimal('15.00'),
        }

        taxa_entrega = taxas_entrega.get(
            endereco.cidade
        )

        if taxa_entrega is None:
            messages.error(
                request,
                'Não realizamos entregas para esta cidade.'
            )

            return redirect('finalizar_pedido')

        subtotal = sum(
            item.subtotal
            for item in itens
        )

        total = subtotal + taxa_entrega

        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                endereco=endereco,
                taxa_entrega=taxa_entrega,
                valor_total=total
            )

            for item in itens:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item.produto,
                    quantidade=item.quantidade,
                    preco_unitario=item.produto.preco
                )

            itens.delete()

        context = {
            'pedido': pedido
        }

        return render(request, 'privado/sucesso.html', context)

    subtotal = sum(
        item.subtotal
        for item in itens
    )

    context = {
        'itens': itens,
        'total': subtotal,
        'enderecos': enderecos,
    }

    return render(request, 'privado/finalizar_pedido.html', context)


@login_required
def sucesso(request):
    return render(request, 'privado/sucesso.html')

@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em')

    context = {
        'pedidos': pedidos
    }

    return render(request, 'privado/meus_pedidos.html', context)

@login_required
def pedido_detalhes(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    subtotal = pedido.valor_total - pedido.taxa_entrega

    context = {
        'pedido': pedido,
        'subtotal': subtotal,
    }

    return render(request, 'privado/pedido_detalhes.html', context)