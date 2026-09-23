from django.urls import path

from .views import (
    produtos,
    produto_gerenciar,
    produto_editar,
    produto_remover,
    produto_detalhes,
    carrinhocompras,
    adicionar_produto,
    remover_produto,
    aumentar_quantidade,
    diminuir_quantidade,
)


urlpatterns = [
    path('produtos/', produtos, name='produtos'),
    path('produto/<int:id>/', produto_detalhes, name='produto_detalhes'),

    path('produto_gerenciar/', produto_gerenciar, name='produto_gerenciar'),
    path('produto_editar/<int:id>/', produto_editar, name='produto_editar'),
    path('produto_remover/<int:id>/', produto_remover, name='produto_remover'),

    path('carrinho/', carrinhocompras, name='carrinhocompras'),
    path('adicionar/<int:produto_id>/', adicionar_produto, name='adicionar_produto'),
    path('remover/<int:item_id>/', remover_produto, name='remover_produto'),
    path('aumentar/<int:item_id>/', aumentar_quantidade, name='aumentar_quantidade'),
    path('diminuir/<int:item_id>/', diminuir_quantidade, name='diminuir_quantidade'),
]