# src/models/recommender.py
import pandas as pd
from ..data.preprocessing import preparar_dados

def avaliar_risco_estoque(df, modelo_risco, modelos_tempo=None):
    # Esta função aplica o modelo treinado para avaliar o risco de vencimento
    # de todos os produtos no estoque e determina ações recomendadas

    dados = preparar_dados(df.copy())

    caracteristicas_risco = ['dias_em_estoque', 'unidades_vendidas_90dias', 'estoque_atual', 'vida_util_estimada',
                             'preco', 'eh_sazonal', 'cd_subsecao', 'cd_loja']

    dados['cd_loja'] = dados['cd_loja'].astype(str).astype('category').cat.codes
    dados['cd_subsecao'] = dados['cd_subsecao'].astype(int)

    probs_risco = modelo_risco.predict_proba(dados[caracteristicas_risco])
    dados['probabilidade_vencimento'] = probs_risco[:, 1]

    # Primeiro determinar os dias para ação com base na vida útil e probabilidade
    dados['dias_para_acao'] = dados.apply(
        lambda row: prever_dias_para_acao(row, modelos_tempo), axis=1
    )

    # Em seguida, determinar a ação recomendada
    dados['acao_recomendada'] = dados.apply(
        lambda row: determinar_acao(row), axis=1
    )

    return dados


def prever_dias_para_acao(row, modelos_tempo=None):
    """
    Calcula quantos dias restam até que seja necessário tomar uma ação.
    """

    if row['vida_util_restante'] <= 0:
        return 0  # já venceu → ação imediata
    elif row['vida_util_restante'] <= 30:
        return 0  # vida útil crítica → ação imediata
    elif row['vida_util_restante'] <= 40:
        return 7  # vida útil em alerta → ação em 7 dias
    elif row['vida_util_restante'] < 100 and row['probabilidade_vencimento'] > 0.5:
        return 14  # risco moderado → ação em 14 dias
    else:
        # Produtos com baixo risco
        return min(60, int(row['vida_util_restante'] * 0.7))



def determinar_acao(row):
    # Esta função determina a ação mais adequada para cada produto
    # baseada na vida útil restante e probabilidade de vencimento

    # Produto já vencido
    if row['vida_util_restante'] <= 0:
        return "Produto já vencido - descartar ou ação imediata"

    # Redução imediata de preço se vida útil estiver nos últimos 30 dias
    elif row['vida_util_restante'] <= 30:
        return "Redução imediata de preço 50%+"

    # Planejar promoção se vida útil estiver nos últimos 40 dias
    elif row['vida_util_restante'] <= 40:
        return "Planejar promoção nos próximos 7 dias"

    # Produtos com vida útil maior mas alta probabilidade de vencimento
    elif row['vida_util_restante'] < 100 and row['probabilidade_vencimento'] > 0.5:
        return "Incluir na promoção semanal"

    # Produtos com baixo risco de vencimento
    else:
        return "Monitorar e reavaliar em 14 dias"