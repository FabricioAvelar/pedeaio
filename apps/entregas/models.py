
from django.db import models
from django.utils import timezone

from apps.pedidos.models import Pedido


class Entrega(models.Model):
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='entrega'
    )
    data_saida = models.DateTimeField(
        null=True,
        blank=True
    )
    data_conclusao = models.DateTimeField(
        null=True,
        blank=True
    )
    observacoes = models.TextField(
        blank=True,
        default=''
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def iniciar_entrega(self):
        self.data_saida = timezone.now()
        self.save(update_fields=['data_saida'])

    def concluir_entrega(self):
        self.data_conclusao = timezone.now()
        self.save(update_fields=['data_conclusao'])

    def __str__(self):
        return f'Entrega do pedido #{self.pedido.id}'
