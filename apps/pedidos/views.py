from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

# Usuário
from apps.usuarios.models import Endereco
from apps.produtos.models import Carrinho, ItemCarrinho
from .models import Pedido, ItemPedido


@login_required
def finalizar_pedido(request):
    carrinho = get_object_or_404(Carrinho,usuario=request.user)

    itens = ItemCarrinho.objects.filter(carrinho=carrinho)

    if not itens.exists():
        messages.error(
            request,
            'Seu carrinho está vazio.'
        )

        return redirect('carrinhocompras')

    endereco = Endereco.objects.filter(usuario=request.user).first()

    if not endereco:
        messages.info(
            request,
            'Cadastre um endereço para continuar.'
        )

        return redirect('endereco_cadastrar')

    total = sum(
        item.subtotal
        for item in itens
    )

    with transaction.atomic():
        pedido = Pedido.objects.create(
            usuario=request.user,
            endereco=endereco,
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
    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        usuario=request.user
    )

    context = {
        'pedido': pedido
    }

    return render(request, 'privado/pedido_detalhes.html', context)