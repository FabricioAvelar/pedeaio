from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme


# Usuário
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


    context = {
        'form': form
    }


    return render(
        request, 'privado/register.html',
        context
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


            proxima_pagina = request.POST.get('next')


            if proxima_pagina and url_has_allowed_host_and_scheme(
                proxima_pagina,
                allowed_hosts={request.get_host()}
            ):
                return redirect(proxima_pagina)


            return redirect('index')


        messages.error(
            request, 'Usuário ou senha incorretos.'
        )


    return render(request, 'privado/login.html')

def sair(request):
    logout(request)
    return redirect('index')

def index(request):
    return render(request, 'index.html')
