from django.db import models
from django.utils import timezone

from apps.usuarios.models import Usuario, Endereco
from apps.produtos.models import Produto


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Preparando', 'Preparando'),
        ('Pronto para entrega', 'Pronto para entrega'),
        ('Saiu para entrega', 'Saiu para entrega'),
        ('Entregue', 'Entregue'),
        ('Cancelado', 'Cancelado'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('Pix', 'Pix'),
        ('Cartão', 'Cartão (na entrega)'),
        ('Dinheiro', 'Dinheiro (na entrega)'),
    ]

    # de qual status o pedido pode ir para quais
    TRANSICOES = {
        'Pendente': ['Preparando', 'Cancelado'],
        'Preparando': ['Pronto para entrega', 'Cancelado'],
        'Pronto para entrega': ['Saiu para entrega', 'Cancelado'],
        'Saiu para entrega': ['Entregue'],
        'Entregue': [],
        'Cancelado': [],
    }

    # etapas mostradas na linha do tempo do cliente
    ETAPAS = ['Pendente', 'Preparando', 'Pronto para entrega',
              'Saiu para entrega', 'Entregue']

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='pedidos'
    )
    endereco = models.ForeignKey(
        Endereco, on_delete=models.PROTECT, related_name='pedidos'
    )
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    taxa_entrega = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default='Pendente'
    )
    forma_pagamento = models.CharField(
        max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True, default=''
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    # NOVOS
    pago = models.BooleanField(default=False)
    pago_em = models.DateTimeField(null=True, blank=True)
    troco_para = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    entregador = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='entregas', limit_choices_to={'is_entregador': True},
    )

    @property
    def subtotal(self):
        return self.valor_total - self.taxa_entrega

    @property
    def etapas(self):
        """Lista usada na linha do tempo (vazia se cancelado)."""
        if self.status == 'Cancelado':
            return []
        atual = self.ETAPAS.index(self.status)
        return [
            {'nome': nome, 'feita': i < atual, 'atual': i == atual}
            for i, nome in enumerate(self.ETAPAS)
        ]

    def mudar_status(self, novo_status, usuario=None):
        if novo_status not in self.TRANSICOES.get(self.status, []):
            raise ValueError(
                f'Não é possível ir de {self.status} para {novo_status}.'
            )
        self.status = novo_status
        self.save(update_fields=['status'])
        HistoricoStatus.objects.create(
            pedido=self, status=novo_status, alterado_por=usuario
        )

    def marcar_como_pago(self):
        self.pago = True
        self.pago_em = timezone.now()
        self.save(update_fields=['pago', 'pago_em'])

    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario.username}'


class HistoricoStatus(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='historico'
    )
    status = models.CharField(max_length=30)
    alterado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'#{self.pedido_id} → {self.status}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'