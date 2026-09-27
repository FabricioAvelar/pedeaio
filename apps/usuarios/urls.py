from django.urls import path
from .views import meus_dados, endereco_cadastrar, editar_perfil, dados_pessoais, meus_enderecos

urlpatterns = [
    path('meus_dados/', meus_dados, name='meus_dados'),
    path('dados_pessoais/', dados_pessoais, name='dados_pessoais'),
    path('editar_perfil/', editar_perfil, name='editar_perfil'),
    
    path('enderecos/', meus_enderecos, name='meus_enderecos'),
    path('endereco/cadastrar/', endereco_cadastrar, name='endereco_cadastrar'),
]