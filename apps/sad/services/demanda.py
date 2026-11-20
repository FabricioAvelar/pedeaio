import math
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import ExtractHour, ExtractWeekDay
from django.utils import timezone

from apps.pedidos.models import Pedido

# Parâmetros da análise (ajuste conforme a realidade do estabelecimento)
PERIODO_DIAS = 30
ENTREGAS_POR_ENTREGADOR_HORA = 3   # quantas entregas um entregador consegue fazer por hora

# ExtractWeekDay do Django: 1 = domingo ... 7 = sábado
DIAS_SEMANA = {1: 'Domingo', 2: 'Segunda', 3: 'Terça', 4: 'Quarta', 5: 'Quinta', 6: 'Sexta', 7: 'Sábado'}
ORDEM_SEMANA = [2, 3, 4, 5, 6, 7, 1]


def analise(dias=PERIODO_DIAS, capacidade=ENTREGAS_POR_ENTREGADOR_HORA):
    desde = timezone.now() - timedelta(days=dias)

    linhas = (
        Pedido.objects
        .exclude(status='Cancelado')
        .filter(criado_em__gte=desde)
        .annotate(dia=ExtractWeekDay('criado_em'), hora=ExtractHour('criado_em'))
        .values('dia', 'hora')
        .annotate(qtd=Count('id'))
    )

    por_hora = [0] * 24
    por_dia = {dia: 0 for dia in DIAS_SEMANA}
    melhor_hora = {}   # dia da semana -> (hora, quantidade)

    for linha in linhas:
        por_hora[linha['hora']] += linha['qtd']
        por_dia[linha['dia']] += linha['qtd']

        atual = melhor_hora.get(linha['dia'])
        if atual is None or linha['qtd'] > atual[1]:
            melhor_hora[linha['dia']] = (linha['hora'], linha['qtd'])

    semanas = dias / 7
    picos = []
    for dia in ORDEM_SEMANA:
        if dia not in melhor_hora:
            continue
        hora, qtd = melhor_hora[dia]
        media_semanal = qtd / semanas
        picos.append({
            'dia': DIAS_SEMANA[dia],
            'faixa': f'{hora:02d}h–{(hora + 1) % 24:02d}h',
            'hora': hora,
            'pedidos': qtd,
            'media_semanal': round(media_semanal, 1),
            'entregadores': max(1, math.ceil(media_semanal / capacidade)),
        })

    # Os picos mais fortes primeiro
    picos.sort(key=lambda p: p['pedidos'], reverse=True)

    total = sum(por_hora)
    hora_pico = por_hora.index(max(por_hora)) if total else None

    return {
        'picos': picos,
        'por_hora': por_hora,
        'por_dia': [{'dia': DIAS_SEMANA[d], 'qtd': por_dia[d]} for d in ORDEM_SEMANA],
        'total': total,
        'hora_pico': hora_pico,
        'dias': dias,
        'capacidade': capacidade,
    }