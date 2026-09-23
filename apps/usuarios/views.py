from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Usuário
from apps.pedidos.models import Pedido
from .forms import EnderecoForm

@login_required
def meus_dados(request):
    if request.user.is_staff:
        return render(request, 'privado/dash_adm.html')

    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).order_by('-criado_em')[:3]

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