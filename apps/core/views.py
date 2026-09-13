from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib import messages

# Usuário
from apps.usuarios.models import Usuario
from apps.produtos.models import Produto, Carrinho, ItemCarrinho 
from .forms import CadastroForm

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

def index(request):
    return render(request, 'index.html')