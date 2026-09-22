from django.urls import path
from .views import *

urlpatterns = [
    path('perfil/', perfil, name='perfil'),
    path('meus_dados/', meus_dados, name='meus_dados'),

    path('endereco/cadastrar/', endereco_cadastrar, name='endereco_cadastrar'),

    path('meus_pedidos/', meus_pedidos, name='meus_pedidos'),
    path('meus_pedidos/<int:pedido_id>/', pedido_detalhes, name='pedido_detalhes'),

]