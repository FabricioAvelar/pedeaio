import hashlib

from django.conf import settings


def gerar_codigo_pix(pedido):
    """Código fictício (demonstração). Fixo para cada pedido: não muda ao recarregar."""
    base = f'{settings.SECRET_KEY}-{pedido.id}-{pedido.valor_total}'
    token = hashlib.sha256(base.encode()).hexdigest()[:28].upper()
    return f'PEDEAIO-PIX-{pedido.id:06d}-{token}'