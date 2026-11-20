from datetime import timedelta

from django.utils import timezone

from apps.pedidos.models import Pedido
from apps.sig.services.entregas import tempo_medio   # reaproveita o cálculo do SIG


# Parâmetros da análise (ajuste conforme a realidade do estabelecimento)
PERIODO_DIAS = 30
LIMITE_CANCELAMENTO = 0.10   # alerta quando mais de 10% dos pedidos são cancelados

# (etapa, status inicial, status final, meta em minutos, o que fazer se passar da meta)
ETAPAS = [
    (
        'Preparo', 'Preparando', 'Pronto para entrega', 20,
        'Cozinha lenta: revisar o tempo de preparo ou reforçar a equipe nos horários de pico.',
    ),
    (
        'Espera pelo entregador', 'Pronto para entrega', 'Saiu para entrega', 10,
        'Pedidos prontos esperando: faltam entregadores ou a atribuição está demorando.',
    ),
    (
        'Rota até o cliente', 'Saiu para entrega', 'Entregue', 25,
        'Entrega demorada: revisar o raio de entrega, a taxa por região ou as rotas.',
    ),
]


def gargalos():
    """Tempo médio por etapa (histórico completo de pedidos entregues).

    Devolve (etapas, nome da etapa gargalo ou None). O gargalo é a etapa
    que mais passou da meta, em porcentagem.
    """
    etapas = []

    for nome, de, ate, meta, dica in ETAPAS:
        media = tempo_medio(de, ate)

        if media is None:
            etapas.append({
                'etapa': nome, 'minutos': None, 'meta': meta, 'acima': False,
                'excesso_pct': 0, 'situacao': 'Sem dados', 'dica': '', 'gargalo': False,
            })
            continue

        minutos = round(media.total_seconds() / 60, 1)
        acima = minutos > meta
        etapas.append({
            'etapa': nome,
            'minutos': minutos,
            'meta': meta,
            'acima': acima,
            'excesso_pct': round((minutos - meta) / meta * 100) if acima else 0,
            'situacao': 'Acima da meta' if acima else 'Dentro da meta',
            'dica': dica if acima else '',
            'gargalo': False,
        })

    acima = [e for e in etapas if e['acima']]
    nome_gargalo = None
    if acima:
        pior = max(acima, key=lambda e: e['excesso_pct'])
        pior['gargalo'] = True
        nome_gargalo = pior['etapa']

    return etapas, nome_gargalo


def cancelamento(dias=PERIODO_DIAS):
    desde = timezone.now() - timedelta(days=dias)
    pedidos = Pedido.objects.filter(criado_em__gte=desde)

    total = pedidos.count()
    cancelados = pedidos.filter(status='Cancelado').count()
    taxa = cancelados / total if total else 0

    return {
        'total': total,
        'cancelados': cancelados,
        'taxa_pct': round(taxa * 100, 1),
        'limite_pct': round(LIMITE_CANCELAMENTO * 100),
        'alerta': taxa > LIMITE_CANCELAMENTO,
    }