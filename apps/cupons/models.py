from django.core.exceptions import ValidationError
from django.db import models


class Cupom(models.Model):
    TIPO_CHOICES = [
        ('percentual', 'Percentual (%)'),
        ('fixo', 'Valor fixo (R$)'),
    ]

    codigo = models.CharField('Código', max_length=30, unique=True)
    descricao = models.CharField('Descrição', max_length=120, blank=True)
    tipo = models.CharField('Tipo de desconto', max_length=10, choices=TIPO_CHOICES)
    valor = models.DecimalField('Valor do desconto', max_digits=8, decimal_places=2)
    valor_minimo = models.DecimalField(
        'Pedido mínimo (R$)', max_digits=8, decimal_places=2, default=0
    )
    valido_ate = models.DateTimeField('Válido até', null=True, blank=True)
    limite_uso = models.PositiveIntegerField(
        'Limite total de usos', null=True, blank=True,
        help_text='Deixe em branco para ilimitado.'
    )
    uso_unico_por_cliente = models.BooleanField('Uma vez por cliente', default=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def clean(self):
        if self.valor is not None:
            if self.valor <= 0:
                raise ValidationError({'valor': 'O desconto deve ser maior que zero.'})
            if self.tipo == 'percentual' and self.valor > 100:
                raise ValidationError({'valor': 'O percentual não pode passar de 100.'})

    def save(self, *args, **kwargs):
        # o código sempre fica em MAIÚSCULAS e sem espaços nas pontas
        self.codigo = self.codigo.strip().upper()
        super().save(*args, **kwargs)

    @property
    def usos(self):
        """Quantos pedidos (não cancelados) já usaram este cupom."""
        return self.pedidos.exclude(status='Cancelado').count()

    @property
    def rotulo_desconto(self):
        if self.tipo == 'percentual':
            return f'{self.valor.normalize():f}% de desconto'
        return f'R$ {self.valor} de desconto'

    def __str__(self):
        return self.codigo