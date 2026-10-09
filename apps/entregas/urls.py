from django.urls import path
from . import views

urlpatterns = [
    path('', views.painel_entregador, name='painel_entregador'),
    path('<int:pedido_id>/aceitar/', views.aceitar_entrega, name='aceitar_entrega'),
    path('<int:pedido_id>/concluir/', views.concluir_entrega, name='concluir_entrega'),
]