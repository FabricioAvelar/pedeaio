from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Carrinho, ItemCarrinho, Foto
from .forms import ProdutoForm

#arquivo = request.FILES['imagem']
#fotos = Foto.objects.all()
#context = {
#    'fotos': fotos
#}
#return render(request, 'index.html', context)
def index(request):
    return render(request, 'index.html', context)

def login(request):
    return render(request, 'login.html', context)

def register(request):
    return render(request, 'register.html, context')

def perfil(request):
    return render(request, 'perfil.html', context)

def produtos(request):
    produtos = Produto.objects.all()

    return render(request, 'produtos.html', {
        'produtos': produtos
    })

def adicionar_produto(request, produto_id):
    if not request.user.is_authenticated:
        return redirect('login')

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

    return redirect('carrinhocompras')

def carrinhocompras(request):
    if not request.user.is_authenticated:
        return redirect('login')

    carrinho, criado = Carrinho.objects.get_or_create(
        usuario=request.user
    )

    itens = ItemCarrinho.objects.filter(carrinho=carrinho)

    total = 0

    for item in itens:
        total += item.produto.preco * item.quantidade

    return render(request,
    'carrinhocompras.html',{
    'itens': itens,
    'total': total})

def aumentar_quantidade(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id)

    item.quantidade += 1
    item.save()

    return redirect('carrinhocompras')

def diminuir_quantidade(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id)

    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    else:
        item.delete()

    return redirect('carrinhocompras')

def remover_produto(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id)
    item.delete()

    return redirect('carrinhocompras')

def finalizar_pedido(request):
    if not request.user.is_authenticated:
        return redirect('login')

    carrinho = get_object_or_404(
        Carrinho,
        usuario=request.user
    )

    ItemCarrinho.objects.filter(
        carrinho=carrinho
    ).delete()

    return redirect('index')

def produto_cadastrar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('produtos')

    else:
        form = ProdutoForm()

    return render(
        request,
        'produto_cadastrar.html',
        {
            'form': form
        }
    )

def batatafrita(request):
    return render(request, 'batata-frita.html', context)

def cachorroquente(request):
    return render(request, 'cachorro_quente.html', context)

def hamburguer(request):
    return render(request, 'hamburguer.html', context)

def pizza(request):
    return render(request, 'pizza.html', context)

def refrigerante(request):
    return render(request, 'refrigerante.html', context)

def salgados(request):
    return render(request, 'salgados.html', context)

def sobremesas(request):
    return render(request, 'sobremesas.html', context)

def sucos(request):
    return render(request, 'sucos.html', context)