from django.urls import path
from . import views

urlpatterns = [
    # cliente
    path('', views.meus_cupons, name='meus_cupons'),
    path('aplicar/', views.aplicar_cupom, name='aplicar_cupom'),
    path('remover/', views.remover_cupom, name='remover_cupom'),

    # administrador
    path('gerenciar/', views.cupom_gerenciar, name='cupom_gerenciar'),
    path('gerenciar/editar/<int:id>/', views.cupom_editar, name='cupom_editar'),
    path('gerenciar/alternar/<int:id>/', views.cupom_alternar, name='cupom_alternar'),
    path('gerenciar/remover/<int:id>/', views.cupom_remover, name='cupom_remover'),
]