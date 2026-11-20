from django.db.models import Count, Max, Sum
from django.utils import timezone

from apps.pedidos.models import Pedido
from apps.usuarios.models import Usuario

# Parâmetros da análise (ajuste conforme a frequência de compra do seu público)
DIAS_EM_RISCO = 30    # sem comprar há mais de 30 dias
DIAS_INATIVO = 60     # sem comprar há mais de 60 dias
LIMITE_LISTA = 10     # quantos clientes aparecem na lista de reativação


def analise():
    agora = timezone.now()

    compras = (
        Pedido.objects
        .exclude(status='Cancelado')
        .filter(usuario__is_staff=False, usuario__is_entregador=False)
        .values('usuario_id', 'usuario__first_name', 'usuario__email')
        .annotate(ultima=Max('criado_em'), pedidos=Count('id'), total=Sum('valor_total'))
    )

    resumo = {'ativos': 0, 'em_risco': 0, 'inativos': 0}
    reativar = []
    com_compra = set()

    for compra in compras:
        com_compra.add(compra['usuario_id'])
        dias = (agora - compra['ultima']).days

        if dias <= DIAS_EM_RISCO:
            resumo['ativos'] += 1
            continue

        if dias <= DIAS_INATIVO:
            resumo['em_risco'] += 1
            segmento = 'Em risco'
            sugestao = 'Enviar um lembrete ou um cupom leve.'
        else:
            resumo['inativos'] += 1
            segmento = 'Inativo'
            sugestao = 'Oferecer um cupom de retorno.'

        reativar.append({
            'nome': compra['usuario__first_name'] or compra['usuario__email'],
            'email': compra['usuario__email'],
            'segmento': segmento,
            'dias_sem_comprar': dias,
            'pedidos': compra['pedidos'],
            'total': compra['total'],
            'sugestao': sugestao,
        })

    # Quem mais gastou e sumiu vem primeiro
    reativar.sort(key=lambda c: c['total'], reverse=True)

    nunca_compraram = (
        Usuario.objects
        .filter(is_staff=False, is_entregador=False)
        .exclude(pk__in=com_compra)
        .count()
    )

    return {
        'resumo': resumo,
        'a_reativar': resumo['em_risco'] + resumo['inativos'],
        'lista': reativar[:LIMITE_LISTA],
        'nunca_compraram': nunca_compraram,
        'dias_em_risco': DIAS_EM_RISCO,
        'dias_inativo': DIAS_INATIVO,
    }