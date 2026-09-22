from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib import messages

# Usuário
from .models import Usuario
from .forms import UsuarioForm, EnderecoForm
from apps.pedidos.models import Pedido

@login_required
def perfil(request):
    return render(request, 'privado/perfil.html')

@login_required
def meus_dados(request):
    if request.user.is_staff:
        return render(request, 'privado/dash_adm.html')

    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em')[:3]

    context = {
        'pedidos': pedidos
    }
    return render(request, 'privado/meus_dados.html', context)

@login_required
def endereco_cadastrar(request):
    if request.method == 'POST':
        form = EnderecoForm(request.POST)

        if form.is_valid():
            endereco = form.save(commit=False)
            endereco.usuario = request.user
            endereco.save()

            messages.success(
                request,
                'Endereço cadastrado com sucesso!'
            )

            return redirect('carrinhocompras')
    else:
        form = EnderecoForm()

    context = {
        'form': form
    }

    return render(request, 'privado/endereco_cadastrar.html', context)