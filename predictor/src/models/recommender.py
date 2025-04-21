# src/models/recommender.py
import pandas as pd
from ..data.preprocessing import preparar_dados

def avaliar_risco_estoque(df, modelo_risco, modelos_tempo=None):
    """
    Aplica o modelo treinado para avaliar o risco de vencimento.
    """
    dados = preparar_dados(df.copy())

    caracteristicas_risco = ['vida_util_restante', 'velocidade_vendas', 'dias_cobertura_estoque',
                             'preco', 'eh_sazonal', 'cd_subsecao', 'cd_loja']

    dados['cd_loja'] = dados['cd_loja'].astype(str).astype('category').cat.codes
    dados['cd_subsecao'] = dados['cd_subsecao'].astype(int)

    probs_risco = modelo_risco.predict_proba(dados[caracteristicas_risco])
    dados['probabilidade_vencimento'] = probs_risco[:, 1]

    dados['dias_para_acao'] = dados.apply(
        lambda row: prever_dias_para_acao(row, modelos_tempo), axis=1
    )

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
    if modelos_tempo and row['LM'] in modelos_tempo:
        modelo = modelos_tempo[row['LM']]
        futuro = modelo.make_future_dataframe(periods=90, freq='D')
        previsao = modelo.predict(futuro)
        return int(min(row['dias_cobertura_estoque'], row['vida_util_restante']))
    else:
        if row['probabilidade_vencimento'] > 0.7:
            return min(14, row['vida_util_restante'] * 0.3)
        elif row['probabilidade_vencimento'] > 0.4:
            return min(30, row['vida_util_restante'] * 0.5)
        else:
            return min(60, row['vida_util_restante'] * 0.7)


def determinar_acao(row):
    """
    Determina a ação mais adequada para cada produto.
    """
    if row['vida_util_restante'] <= 0:
        return "Produto já vencido - descartar ou ação imediata"

    if row['probabilidade_vencimento'] > 0.8:
        if row['dias_para_acao'] < 7:
            return "Redução imediata de preço 50%+"
        else:
            return "Planejar promoção nos próximos 7 dias"
    elif row['probabilidade_vencimento'] > 0.5:
        if row['secao'] == 'JARDIM':
            return "Transferir para loja com maior giro"
        else:
            return "Incluir na promoção semanal"
    else:
        return "Monitorar e reavaliar em 14 dias"
