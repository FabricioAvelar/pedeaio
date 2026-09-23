from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# Usuário
from .models import Produto, Carrinho, ItemCarrinho
from .forms import ProdutoForm


@login_required
def produto_gerenciar(request):
    if not request.user.is_staff:
        return redirect('index')

    if request.method == 'POST':
        form = ProdutoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            return redirect('produto_gerenciar')

    else:
        form = ProdutoForm()

    produtos = Produto.objects.all()

    context = {
        'form': form,
        'produtos': produtos
    }

    return render(request, 'privado/produto_gerenciar.html', context)

@login_required
def produto_editar(request, id):
    if not request.user.is_staff:
        return redirect('index')

    produto = get_object_or_404(
        Produto,
        id=id
    )

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
        form = ProdutoForm(
            instance=produto
        )

    context = {
        'form': form
    }

    return render(request, 'privado/produto_gerenciar.html', context)

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
        produtos = produtos.filter(
            nome__icontains=busca
        )

    if categoria:
        produtos = produtos.filter(
            categoria=categoria
        )

    context = {
        'produtos': produtos,
        'busca': busca,
        'categoria': categoria
    }

    return render(request, 'produtos.html', context)

def produto_detalhes(request, id):
    produto = get_object_or_404(
        Produto,
        id=id
    )

    context = {
        'produto': produto
    }

    return render(request, 'privado/produto_detalhes.html', context)

@login_required
def adicionar_produto(request, produto_id):
    produto = get_object_or_404(
        Produto,
        id=produto_id
    )

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

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'produtos'
        )
    )

@login_required
def carrinhocompras(request):
    carrinho, criado = Carrinho.objects.get_or_create(
        usuario=request.user
    )

    itens = ItemCarrinho.objects.filter(
        carrinho=carrinho
    )

    total = sum(
        item.subtotal
        for item in itens
    )

    context = {
        'itens': itens,
        'total': total
    }

    return render(request, 'privado/carrinhocompras.html', context)

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

def quantidade_carrinho(request):
    if not request.user.is_authenticated:
        return 0

    carrinho = Carrinho.objects.filter(
        usuario=request.user
    ).first()

    if not carrinho:
        return 0

    return ItemCarrinho.objects.filter(
        carrinho=carrinho
    ).count()