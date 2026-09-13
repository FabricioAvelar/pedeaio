from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib import messages

# Usuário
from .models import Usuario
from .forms import UsuarioForm

@login_required
def perfil(request):
    return render(request, 'privado/perfil.html')

@login_required
def meus_dados(request):
    if request.user.is_staff:
        return render(request, 'privado/dash_adm.html')
    return render(request, 'privado/meus_dados.html')