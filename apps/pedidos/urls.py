from django.urls import path
from .views import finalizar_pedido, sucesso, meus_pedidos, pedido_detalhes

urlpatterns = [
    path('finalizar/', finalizar_pedido, name='finalizar_pedido'),
    path('sucesso/', sucesso, name='sucesso'),

    path('meus_pedidos/', meus_pedidos, name='meus_pedidos'),
    path('meus_pedidos/<int:pedido_id>/', pedido_detalhes, name='pedido_detalhes'),
]