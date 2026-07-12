from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    cpf = models.CharField('CPF', max_length=11, primary_key=True)
    email = models.CharField('E-mail', max_length=200, unique=True)
    nascimento = models.DateField('Data de Nascimento')
    def __str__(self):
        return self.username

class Endereco(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rua = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    def __str__(self):
        return f'{self.rua}, {self.numero}'

class Favorito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    produto = models.CharField(max_length=100)
    def __str__(self):
        return self.produto

class Cupom(models.Model):
    codigo = models.CharField(max_length=30)
    desconto = models.IntegerField()
    ativo = models.BooleanField(default=True)
    def __str__(self):
        return self.codigo

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/')

    def __str__(self):
        return self.nome

class Carrinho(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)