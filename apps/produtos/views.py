from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db import transaction

# Usuário
from .models import Produto, Carrinho, ItemCarrinho
from .forms import ProdutoForm
from apps.usuarios.models import Endereco
from apps.pedidos.models import Pedido, ItemPedido


@login_required
def produto_gerenciar(request):
    if not request.user.is_staff:
        return redirect('index')

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('produto_gerenciar')
    else:
        form = ProdutoForm()
    produtos = Produto.objects.all()
    return render(
        request,
        'privado/produto_gerenciar.html',
        {
            'form': form,
            'produtos': produtos
        }
    )

@login_required
def produto_editar(request, id):
    if not request.user.is_staff:
        return redirect('index')

    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        form = ProdutoForm(
            request.POST,
            request.FILES,
            instance=produto
        )
        if form.is_valid():
            form.save()
            return redirect('produto_gerenciar')
    else:
        form = ProdutoForm(instance=produto)
    return render(
        request,
        'privado/produto_gerenciar.html',
        {
            'form': form
        }
    )

@login_required
def produto_remover(request, id):
    if not request.user.is_staff:
        return redirect('index')

    if request.method == 'POST':
        produto = get_object_or_404(
            Produto,
            id=id
        )
        produto.delete()
    return redirect('produto_gerenciar')

def produtos(request):
    produtos = Produto.objects.all()
    busca = request.GET.get('buscar')
    categoria = request.GET.get('categoria')
    if busca:
        produtos = produtos.filter(nome__icontains=busca)

    if categoria:
        produtos = produtos.filter(categoria=categoria)
    return render(request,'produtos.html',{
        'produtos': produtos,
        'busca': busca,
        'categoria': categoria
    })

def produto_detalhes(request, id):
    produto = get_object_or_404(Produto, id=id)

    return render(
        request,
        'produto_detalhes.html',
        {
            'produto': produto
        }
    )

@login_required
def adicionar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho, criado = Carrinho.objects.get_or_create(
        usuario=request.user
    )

    item, criado = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto
    )
    if not criado:
        item.quantidade += 1
        item.save()
    return redirect(request.META.get('HTTP_REFERER', 'produtos'))

@login_required
def carrinhocompras(request):
    carrinho, criado = Carrinho.objects.get_or_create(
        usuario=request.user
    )
    itens = ItemCarrinho.objects.filter(carrinho=carrinho)
    total = 0
    for item in itens:
        total += item.produto.preco * item.quantidade
    return render(
        request,
        'privado/carrinhocompras.html',
        {
            'itens': itens,
            'total': total
        }
    )

@login_required
def aumentar_quantidade(request, item_id):
    item = get_object_or_404(
        ItemCarrinho,
        id=item_id,
        carrinho__usuario=request.user
    )
    item.quantidade += 1
    item.save()
    return redirect('carrinhocompras')

@login_required
def diminuir_quantidade(request, item_id):
    item = get_object_or_404(
        ItemCarrinho,
        id=item_id,
        carrinho__usuario=request.user
    )
    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    else:
        item.delete()
    return redirect('carrinhocompras')

@login_required
def remover_produto(request, item_id):
    item = get_object_or_404(
        ItemCarrinho,
        id=item_id,
        carrinho__usuario=request.user
    )
    item.delete()
    return redirect('carrinhocompras')

@login_required
def finalizar_pedido(request):
    carrinho = get_object_or_404(
        Carrinho,
        usuario=request.user
    )

    itens = ItemCarrinho.objects.filter(carrinho=carrinho)

    if not itens.exists():
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('carrinhocompras')

    print('USUÁRIO LOGADO:', request.user)
    print('CPF LOGADO:', request.user.cpf)
    print('ENDEREÇOS NO BANCO:', Endereco.objects.all())
    print(
        'ENDEREÇOS DO USUÁRIO:',
        Endereco.objects.filter(usuario=request.user)
    )

    endereco = Endereco.objects.filter(
        usuario=request.user
    ).first()

    if not endereco:
        messages.info(
            request,
            'Cadastre um endereço para continuar.'
        )
        return redirect('endereco_cadastrar')

    total = sum(item.subtotal for item in itens)

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

def sucesso(request):
    return render(request, 'privado/sucesso.html')

def quantidade_carrinho(request):
    if not request.user.is_authenticated:
        return 0
    carrinho = Carrinho.objects.filter(usuario=request.user).first()
    if not carrinho:
        return 0
    return ItemCarrinho.objects.filter(carrinho=carrinho).count()