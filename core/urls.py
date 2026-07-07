from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('perfil/', perfil, name='perfil'),
    path('produtos/', produtos, name='produtos'),

    path('adicionar/<int:produto_id>/', adicionar_produto, name='adicionar_produto'),
    path('remover/<int:item_id>/', remover_produto, name='remover_produto'),
    path('aumentar/<int:item_id>/', aumentar_quantidade, name='aumentar_quantidade'),
    path('diminuir/<int:item_id>/', diminuir_quantidade, name='diminuir_quantidade'),
    path('finalizar/', finalizar_pedido, name='finalizar_pedido'),

    path('produto/cadastrar/', produto_cadastrar, name='produto_cadastrar'),
    path('batata-frita/', batatafrita, name='batata-frita'),
    path('cachorro_quente/', cachorroquente, name='cachorro_quente'),
    path('hamburguer/', hamburguer, name='hamburguer'),
    path('pizza/', pizza, name='pizza'),
    path('refrigerante/', refrigerante, name='refrigerante'),
    path('salgados/', salgados, name='salgados'),
    path('sobremesas/', sobremesas, name='sobremesas'),
    path('sucos/', sucos, name='sucos'),
] 
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)