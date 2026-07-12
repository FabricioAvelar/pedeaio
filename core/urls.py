from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('perfil/', perfil, name='perfil'),
    path('produtos/', produtos, name='produtos'),

    path('produto_gerenciar/', produto_gerenciar, name='produto_gerenciar'),
    path('produto_editar/<int:id>/', produto_editar, name='produto_editar'),
    path('produto_remover/<int:id>/', produto_remover, name='produto_remover'),


    path('adicionar/<int:produto_id>/', adicionar_produto, name='adicionar_produto'),
    path('remover/<int:item_id>/', remover_produto, name='remover_produto'),
    path('aumentar/<int:item_id>/', aumentar_quantidade, name='aumentar_quantidade'),
    path('diminuir/<int:item_id>/', diminuir_quantidade, name='diminuir_quantidade'),
    path('finalizar/', finalizar_pedido, name='finalizar_pedido'),

]