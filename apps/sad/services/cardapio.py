from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils import timezone

from apps.pedidos.models import ItemPedido
from apps.produtos.models import Produto

# Parâmetros da análise (ajuste conforme a realidade do estabelecimento)
PERIODO_DIAS = 30
LIMITE_A = Decimal('0.70')   # produtos que, juntos, somam até 70% da receita
LIMITE_B = Decimal('0.90')   # até 90%; o restante é classe C

RECEITA = ExpressionWrapper(
    F('quantidade') * F('preco_unitario'),
    output_field=DecimalField(max_digits=12, decimal_places=2),
)


def _vendas_por_produto(dias):
    desde = timezone.now() - timedelta(days=dias)
    linhas = (
        ItemPedido.objects
        .exclude(pedido__status='Cancelado')
        .filter(pedido__criado_em__gte=desde)
        .values('produto_id')
        .annotate(qtd=Sum('quantidade'), receita=Sum(RECEITA))
    )
    return {linha['produto_id']: linha for linha in linhas}


def _acao(classe, disponivel, dias):
    """Devolve (ação, observação) para o produto."""
    if classe == 'A':
        if not disponivel:
            return 'Destaque', 'Campeão de receita, mas indisponível: repor com prioridade.'
        return 'Destaque', 'Manter em destaque e garantir que não falte.'

    if not disponivel:
        return 'Revisar', 'Indisponível: decidir se volta ao cardápio ou sai de vez.'

    if classe == 'B':
        return 'Manter', 'Desempenho estável: manter no cardápio.'

    if classe == 'C':
        return 'Promover', 'Receita baixa: testar promoção, combo ou novo destaque.'

    return 'Revisar', f'Sem vendas em {dias} dias: reformular, divulgar ou retirar do cardápio.'


def analise(dias=PERIODO_DIAS):
    vendas = _vendas_por_produto(dias)

    linhas = []
    for produto in Produto.objects.select_related('categoria'):
        venda = vendas.get(produto.id)
        linhas.append({
            'produto': produto.nome,
            'categoria': produto.categoria.nome if produto.categoria else '—',
            'disponivel': produto.disponivel,
            'qtd': venda['qtd'] if venda else 0,
            'receita': venda['receita'] if venda else Decimal('0.00'),
        })

    linhas.sort(key=lambda l: l['receita'], reverse=True)
    total = sum((l['receita'] for l in linhas), Decimal('0.00'))

    # Curva ABC: a classe depende de quanto da receita já foi somado ANTES do produto,
    # então o primeiro colocado é sempre A
    acumulado = Decimal('0.00')
    for linha in linhas:
        if linha['receita'] > 0:
            antes = acumulado / total
            linha['classe'] = 'A' if antes < LIMITE_A else 'B' if antes < LIMITE_B else 'C'
            linha['participacao'] = round(float(linha['receita'] / total * 100), 1)
            acumulado += linha['receita']
        else:
            linha['classe'] = '—'
            linha['participacao'] = 0.0

        acao, observacao = _acao(linha['classe'], linha['disponivel'], dias)
        linha['acao'] = acao
        linha['acao_css'] = acao.lower()
        linha['observacao'] = observacao

    resumo = {'destaque': 0, 'manter': 0, 'promover': 0, 'revisar': 0}
    for linha in linhas:
        resumo[linha['acao_css']] += 1

    return {'linhas': linhas, 'resumo': resumo, 'total_receita': total, 'dias': dias}