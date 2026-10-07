from django.db import models
from apps.usuarios.models import Usuario, Endereco
from apps.produtos.models import Produto


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Preparando', 'Preparando'),
        ('Saiu para entrega', 'Saiu para entrega'),
        ('Entregue', 'Entregue'),
        ('Cancelado', 'Cancelado'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('Pix', 'Pix'),
        ('Cartão', 'Cartão (na entrega)'),
        ('Dinheiro', 'Dinheiro (na entrega)'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )

    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.PROTECT,
        related_name='pedidos'
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    taxa_entrega = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pendente'
    )

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        blank=True,
        default=''
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.valor_total - self.taxa_entrega

    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario.username}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )

    quantidade = models.PositiveIntegerField()

    preco_unitario = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'