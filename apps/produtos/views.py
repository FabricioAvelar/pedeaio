from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Usuário
from .models import Produto, Categoria, Carrinho, ItemCarrinho
from .forms import ProdutoForm, CategoriaForm


@login_required
def produto_gerenciar(request):
    if not request.user.is_staff:
        return redirect('index')

    produto_form = ProdutoForm()
    categoria_form = CategoriaForm()

    if request.method == 'POST':
        if 'cadastrar_produto' in request.POST:
            produto_form = ProdutoForm(
                request.POST,
                request.FILES
            )

            if produto_form.is_valid():
                produto_form.save()
                return redirect('produto_gerenciar')

        elif 'cadastrar_categoria' in request.POST:
            categoria_form = CategoriaForm(
                request.POST
            )

            if categoria_form.is_valid():
                categoria_form.save()
                return redirect('produto_gerenciar')

    produtos = Produto.objects.select_related('categoria').all()

    categorias = Categoria.objects.all()

    context = {
        'produto_form': produto_form,
        'categoria_form': categoria_form,
        'produtos': produtos,
        'categorias': categorias
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
        produto_form = ProdutoForm(
            request.POST,
            request.FILES,
            instance=produto
        )

        if produto_form.is_valid():
            produto_form.save()
            return redirect('produto_gerenciar')

    else:
        produto_form = ProdutoForm(
            instance=produto
        )

    categoria_form = CategoriaForm()

    produtos = Produto.objects.select_related('categoria').all()

    categorias = Categoria.objects.all()

    context = {
        'produto_form': produto_form,
        'categoria_form': categoria_form,
        'produtos': produtos,
        'categorias': categorias
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
    busca = request.GET.get('buscar', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()

    categorias = Categoria.objects.all().order_by('nome')

    produtos = Produto.objects.select_related('categoria').all()

    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) |
            Q(descricao__icontains=busca)
        )

    if categoria_id:
        produtos = produtos.filter(
            categoria_id=categoria_id
        )

    categorias_com_produtos = []

    for categoria in categorias:
        produtos_categoria = produtos.filter(
            categoria=categoria
        )

        if produtos_categoria.exists():
            categorias_com_produtos.append({
                'categoria': categoria,
                'produtos': produtos_categoria
            })

    context = {
        'categorias': categorias,
        'categorias_com_produtos': categorias_com_produtos,
        'busca': busca,
        'categoria': categoria_id
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

    return render(request, 'produto_detalhes.html', context)

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