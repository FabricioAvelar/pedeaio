from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def perfil(request):
    return render(request, 'perfil.html')

def promocoes(request):
    return render(request, 'promocoes.html')

def carrinhocompras(request):
    return render(request, 'carrinhocompras.html')

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