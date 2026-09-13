from django.db import models
from apps.usuarios.models import Usuario

class Produto(models.Model):
    CATEGORIAS = [
        ('Hamburguer', 'Hamburguer'),
        ('Cachorro quente', 'Cachorro quente'),
        ('Pizza', 'Pizza'),
        ('Batata', 'Batata'),
        ('Bebida', 'Bebida'),
        ('Sobremesa', 'Sobremesa'),
        ('Salgado', 'Salgado'),
    ]
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    imagem = models.ImageField(upload_to='produtos/')

class Carrinho(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)

    @property
    def subtotal(self):
        return self.produto.preco * self.quantidade

