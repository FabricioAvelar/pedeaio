from django.urls import path
from .views import (
    meus_dados,
    dados_pessoais,
    editar_perfil,
    meus_enderecos,
    endereco_cadastrar,
    endereco_editar,
    endereco_excluir,
    dashboard,
)

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),

    path('meus_dados/', meus_dados, name='meus_dados'),
    path('dados_pessoais/', dados_pessoais, name='dados_pessoais'),
    path('editar_perfil/', editar_perfil, name='editar_perfil'),
    
    path('enderecos/', meus_enderecos, name='meus_enderecos'),
    path('endereco/cadastrar/', endereco_cadastrar, name='endereco_cadastrar'),
    path('endereco/<int:endereco_id>/editar/', endereco_editar, name='endereco_editar'),
    path('endereco/<int:endereco_id>/excluir/', endereco_excluir, name='endereco_excluir'),
    
]