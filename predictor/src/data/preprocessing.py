# src/data/preprocessing.py
import numpy as np
import pandas as pd

def preparar_dados(df):
    """
    Transforma os dados brutos em features utilizáveis pelo modelo.
    """
    # Converter datas para datetime
    df['data_recebimento'] = pd.to_datetime(df['data_recebimento'], format="%Y-%m-%d %H:%M")

    # Calcular variáveis derivadas
    df['dias_em_estoque'] = (pd.Timestamp.now() - df['data_recebimento']).dt.days
    df['vida_util_estimada'] = df['vida_util_subsecao']
    df['vida_util_restante'] = df['vida_util_estimada'] - df['dias_em_estoque']
    df['velocidade_vendas'] = df['unidades_vendidas_90dias'] / 90
    df['dias_cobertura_estoque'] = df['estoque_atual'] / df['velocidade_vendas'].replace(0, np.nan)
    df['indice_risco'] = df['dias_cobertura_estoque'] / df['vida_util_restante'].replace(0, np.nan)

    # Variável alvo
    df['vai_vencer'] = (df['indice_risco'] > 1.0) | (df['vida_util_restante'] <= 0)

    return df
