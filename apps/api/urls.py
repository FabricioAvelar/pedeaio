from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import *

urlpatterns = [
    # Autenticação (JWT). No login, o campo "username" recebe o e-mail.
    path('token/', LoginView.as_view(), name='api_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='api_token_blacklist'),

    # Usuários
    path('cadastro/', cadastro, name='api_cadastro'),
    path('eu/', eu, name='api_eu'),

    # Endereços
    path('enderecos/', enderecos, name='api_enderecos'),
    path('endereco_atualizar/<int:id>/', endereco_atualizar, name='api_endereco_atualizar'),
    path('endereco_deletar/<int:id>/', endereco_deletar, name='api_endereco_deletar'),

    # Categorias
    path('categorias/', categorias, name='api_categorias'),
    path('categoria_atualizar/<int:id>/', categoria_atualizar, name='api_categoria_atualizar'),
    path('categoria_deletar/<int:id>/', categoria_deletar, name='api_categoria_deletar'),

    # Produtos
    path('produtos/', produtos, name='api_produtos'),
    path('produto_detalhes/<int:id>/', produto_detalhes, name='api_produto_detalhes'),
    path('produto_atualizar/<int:id>/', produto_atualizar, name='api_produto_atualizar'),
    path('produto_deletar/<int:id>/', produto_deletar, name='api_produto_deletar'),

    # Carrinho
    path('carrinho/', carrinho, name='api_carrinho'),
    path('carrinho_adicionar/<int:produto_id>/', carrinho_adicionar, name='api_carrinho_adicionar'),
    path('carrinho_aumentar/<int:item_id>/', carrinho_aumentar, name='api_carrinho_aumentar'),
    path('carrinho_diminuir/<int:item_id>/', carrinho_diminuir, name='api_carrinho_diminuir'),
    path('carrinho_remover/<int:item_id>/', carrinho_remover, name='api_carrinho_remover'),

    # Pedidos
    path('pedidos/', pedidos, name='api_pedidos'),

    # Entregas
    path('entregas/', entregas, name='api_entregas'),
    path('entregas/<int:pedido_id>/aceitar/', aceitar_entrega, name='api_aceitar_entrega'),
    path('entregas/<int:pedido_id>/concluir/', concluir_entrega, name='api_concluir_entrega'),
]