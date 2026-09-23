from django.urls import path
from .views import meus_dados, endereco_cadastrar

urlpatterns = [
    path('meus_dados/', meus_dados, name='meus_dados'),

    path('endereco/cadastrar/', endereco_cadastrar, name='endereco_cadastrar'),
]