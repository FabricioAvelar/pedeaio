from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('perfil/', perfil, name='perfil'),
    path('promocoes/', promocoes, name='promocoes'),
    path('carrinhocompras/', carrinhocompras, name='carrinhocompras'),

    path('batata-frita/', batatafrita, name='batata-frita'),
    path('cachorro_quente/', cachorroquente, name='cachorro_quente'),
    path('hamburguer/', hamburguer, name='hamburguer'),
    path('pizza/', pizza, name='pizza'),
    path('refrigerante/', refrigerante, name='refrigerante'),
    path('salgados/', salgados, name='salgados'),
    path('sobremesas/', sobremesas, name='sobremesas'),
    path('sucos/', sucos, name='sucos'),
]