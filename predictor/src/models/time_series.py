# src/models/time_series.py
import pandas as pd
from prophet import Prophet

def treinar_modelo_tempo_vencimento(dados):
    """
    Utiliza Prophet para prever a velocidade de vendas futura.
    """
    modelos_vencimento = {}

    for lm in dados['LM'].unique():
        dados_produto = dados[dados['LM'] == lm].copy()
        dados_produto['data'] = pd.to_datetime(dados_produto['data_recebimento'])

        if len(dados_produto) >= 30:
            df_prophet = pd.DataFrame({
                'ds': dados_produto['data'],
                'y': dados_produto['velocidade_vendas']
            })
            modelo = Prophet(seasonality_mode='multiplicative')
            modelo.fit(df_prophet)
            modelos_vencimento[lm] = modelo

    return modelos_vencimento
