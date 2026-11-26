from django.db import models

from apps.usuarios.models import Usuario
from apps.produtos.models import Produto


class Favorito(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='favoritos'
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, related_name='favoritado_por'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'produto'], name='favorito_unico'
            ),
        ]

    def __str__(self):
        return f'{self.usuario.username} ♥ {self.produto.nome}'