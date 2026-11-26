from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.utils import timezone

from .models import Cupom

SESSION_KEY = 'cupom_codigo'
ZERO = Decimal('0.00')


class CupomInvalido(Exception):
    """Levantada com a mensagem que deve ser mostrada ao cliente."""


def calcular_desconto(cupom, subtotal):
    if cupom.tipo == 'percentual':
        desconto = subtotal * cupom.valor / Decimal('100')
    else:
        desconto = cupom.valor

    desconto = desconto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # desconto só nos produtos: nunca passa do subtotal (o frete não entra)
    return min(desconto, subtotal)


def validar_cupom(codigo, usuario, subtotal, travar=False):
    """
    Confere todas as regras. Devolve (cupom, desconto) ou levanta CupomInvalido.
    travar=True bloqueia o cupom (usar dentro de transaction.atomic()).
    """
    codigo = (codigo or '').strip().upper()

    if not codigo:
        raise CupomInvalido('Digite o código do cupom.')

    consulta = Cupom.objects.select_for_update() if travar else Cupom.objects

    try:
        cupom = consulta.get(codigo=codigo)
    except Cupom.DoesNotExist:
        raise CupomInvalido('Cupom não encontrado.')

    if not cupom.ativo:
        raise CupomInvalido('Este cupom não está mais ativo.')

    if cupom.valido_ate and cupom.valido_ate < timezone.now():
        raise CupomInvalido('Este cupom expirou.')

    if cupom.limite_uso is not None and cupom.usos >= cupom.limite_uso:
        raise CupomInvalido('Este cupom atingiu o limite de usos.')

    if cupom.uso_unico_por_cliente and cupom.pedidos.filter(
        usuario=usuario
    ).exclude(status='Cancelado').exists():
        raise CupomInvalido('Você já usou este cupom.')

    if subtotal < cupom.valor_minimo:
        raise CupomInvalido(
            f'Este cupom exige um pedido mínimo de R$ {cupom.valor_minimo}.'
        )

    return cupom, calcular_desconto(cupom, subtotal)


def cupom_da_sessao(request, subtotal):
    """
    Cupom aplicado na sessão, revalidado a cada uso.
    Se deixou de valer, é removido. Devolve (cupom, desconto).
    """
    codigo = request.session.get(SESSION_KEY)

    # sem cupom na sessão, ou carrinho vazio: nada a calcular
    if not codigo or not subtotal:
        return None, ZERO

    try:
        return validar_cupom(codigo, request.user, subtotal)
    except CupomInvalido as erro:
        request.session.pop(SESSION_KEY, None)
        messages.warning(request, f'O cupom {codigo} foi removido: {erro}')
        return None, ZERO