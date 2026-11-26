from django.urls import path
from . import views

urlpatterns = [
    path('', views.meus_favoritos, name='meus_favoritos'),
    path('alternar/<int:produto_id>/', views.alternar_favorito, name='alternar_favorito'),
]