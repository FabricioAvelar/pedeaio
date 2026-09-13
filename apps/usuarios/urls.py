from django.urls import path
from .views import *

urlpatterns = [
    path('perfil/', perfil, name='perfil'),
    path('meus_dados/', meus_dados, name='meus_dados'),
]