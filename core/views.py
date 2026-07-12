from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Carrinho, ItemCarrinho
from .forms import ProdutoForm

# Usuário
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages



def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario:
            auth_login(request, usuario)
            return redirect('index')

        messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def perfil(request):
    return render(request, 'perfil.html')


def produto_gerenciar(request):

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
        'produto_gerenciar.html',
        {
            'form': form,
            'produtos': produtos
        }
    )

def produto_editar(request, id):
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
        'produto_gerenciar.html',
        {
            'form': form
        }
    )


def produto_remover(request, id):

    if request.method == 'POST':

        produto = get_object_or_404(
            Produto,
            id=id
        )

        produto.delete()

    return redirect('produto_gerenciar')






def produtos(request):
    produtos = Produto.objects.all()

    return render(request, 'produtos.html', {
        'produtos': produtos
    })


def adicionar_produto(request, produto_id):
    # if not request.user.is_authenticated:
    #    return redirect('login')

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







def batatafrita(request):
    return render(request, 'batata-frita.html')

def cachorroquente(request):
    return render(request, 'cachorro_quente.html')

def hamburguer(request):
    return render(request, 'hamburguer.html')

def pizza(request):
    return render(request, 'pizza.html')

def refrigerante(request):
    return render(request, 'refrigerante.html')

def salgados(request):
    return render(request, 'salgados.html')

def sobremesas(request):
    return render(request, 'sobremesas.html')

def sucos(request):
    return render(request, 'sucos.html')