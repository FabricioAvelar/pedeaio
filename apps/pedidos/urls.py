from django.urls import path
from .views import (
    carrinhocompras,
    adicionar_produto,
    remover_produto,
    aumentar_quantidade,
    diminuir_quantidade,
    finalizar_pedido,
    sucesso,
    meus_pedidos,
    pedido_detalhes,
    pagar,
    pedido_status,
)

urlpatterns = [
    path('carrinho/', carrinhocompras, name='carrinhocompras'),
    path('adicionar/<int:produto_id>/', adicionar_produto, name='adicionar_produto'),
    path('remover/<int:item_id>/', remover_produto, name='remover_produto'),
    path('aumentar/<int:item_id>/', aumentar_quantidade, name='aumentar_quantidade'),
    path('diminuir/<int:item_id>/', diminuir_quantidade, name='diminuir_quantidade'),

    path('finalizar/', finalizar_pedido, name='finalizar_pedido'),
    path('sucesso/', sucesso, name='sucesso'),

    path('meus_pedidos/', meus_pedidos, name='meus_pedidos'),
    path('meus_pedidos/<int:pedido_id>/', pedido_detalhes, name='pedido_detalhes'),
    path('meus_pedidos/<int:pedido_id>/status/', pedido_status, name='pedido_status'),

    path('<int:pedido_id>/pagamento/', pagar, name='pagamento'),
]