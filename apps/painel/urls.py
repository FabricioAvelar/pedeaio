from django.urls import path
from . import views

urlpatterns = [
    path('pedidos/', views.pedidos_lista, name='painel_pedidos'),
    path('pedidos/<int:pedido_id>/', views.pedido_gerenciar, name='painel_pedido'),
    path('pedidos/<int:pedido_id>/status/', views.alterar_status, name='painel_alterar_status'),
    path('pedidos/<int:pedido_id>/pagamento/confirmar/', views.confirmar_pagamento, name='painel_confirmar_pagamento'),
]