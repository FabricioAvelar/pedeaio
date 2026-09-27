from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError

# Pedidos
from apps.pedidos.models import Pedido

# Usuários
from .models import Endereco
from .forms import EnderecoForm, UsuarioEditarForm

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

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = UsuarioEditarForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()

            messages.success(request, 'Dados atualizados com sucesso!')

            return redirect('dados_pessoais')

    else:
        form = UsuarioEditarForm(
            instance=request.user
        )

    context = {
        'form': form
    }

    return render(request, 'privado/editar_perfil.html', context)

@login_required
def dados_pessoais(request):
    enderecos = request.user.enderecos.all()

    context = {
        'enderecos': enderecos,
    }

    return render(request, 'privado/dados_pessoais.html', context)

@login_required
def meus_enderecos(request):
    enderecos = request.user.enderecos.all()

    context = {
        'enderecos': enderecos,
    }

    return render(request, 'privado/meus_enderecos.html', context)

@login_required
def endereco_editar(request, endereco_id):
    endereco = get_object_or_404(
        Endereco,
        id=endereco_id,
        usuario=request.user
    )

    if request.method == 'POST':
        form = EnderecoForm(
            request.POST,
            instance=endereco
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Endereço atualizado com sucesso!'
            )

            return redirect('meus_enderecos')

    else:
        form = EnderecoForm(instance=endereco)

    context = {
        'form': form,
        'endereco': endereco,
    }

    return render(request, 'privado/endereco_editar.html', context)

@login_required
def endereco_excluir(request, endereco_id):
    endereco = get_object_or_404(
        Endereco,
        id=endereco_id,
        usuario=request.user
    )

    if request.method == 'POST':
        try:
            endereco.delete()

            messages.success(
                request,
                'Endereço excluído com sucesso!'
            )

        except ProtectedError:
            messages.error(
                request,
                'Este endereço não pode ser excluído porque está vinculado a um ou mais pedidos.'
            )

    return redirect('meus_enderecos')