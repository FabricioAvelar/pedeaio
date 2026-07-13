from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Carrinho, ItemCarrinho, Usuario
from .forms import ProdutoForm, CadastroForm

# Usuário
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib import messages


# Função auxiliar do carrinho

def quantidade_carrinho(request):
    if not request.user.is_authenticated:
        return 0

    carrinho = Carrinho.objects.filter(usuario=request.user).first()

    if not carrinho:
        return 0

    return ItemCarrinho.objects.filter(carrinho=carrinho).count()


# Página Inicial
def index(request):
    return render(request, 'index.html', {
        'quantidade_carrinho': quantidade_carrinho(request)
    })

# Página Inicial #
def index(request):
    return render(request, 'index.html')





# Autenticação #
def register(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            usuario.username = usuario.email
            usuario.save()

            messages.success(
                request,
                'Conta criada com sucesso! Faça seu login.'
            )
            return redirect('login')
    else:
        form = CadastroForm()
    return render(
        request,
        'privado/register.html',
        {
            'form': form
        }
    )

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        usuario = authenticate(
            request,
            username=email,
            password=password
        )
        if usuario:
            auth_login(request, usuario)
            return redirect('index')
        messages.error(request, 'Usuário ou senha incorretos.')
    return render(request, 'privado/login.html')

def sair(request):
    logout(request)
    return redirect('index')





# Perfil #
@login_required
def perfil(request):
    return render(request, 'privado/perfil.html')





# Gerenciamento #
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





# Produtos #
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





# Carrinho de Compras #
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





# Finalizar Pedido #
@login_required
def finalizar_pedido(request):
    carrinho = get_object_or_404(
        Carrinho,
        usuario=request.user
    )
    ItemCarrinho.objects.filter(
        carrinho=carrinho
    ).delete()
    return render(request, 'privado/sucesso.html')

def sucesso(request):
    return render(request, 'privado/sucesso.html')


@login_required
def perfil(request):
    if request.user.is_staff:
        return render(request, 'privado/dashboard_admin.html')

    return render(request, 'privado/perfil.html')






# -------------------------------------- #
# SERÃO ADICIONADAS EM VERSÕES FUTURAS:
# Página para Entregador
# Formas de Pagamento
# Endereço e taxa de entrega
# Rastreamento
# Nota fiscal
# -------------------------------------- #