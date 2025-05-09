# src/models/risk_classifier.py
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score, KFold

def treinar_modelo_risco(dados):
    # Esta função treina um modelo XGBoost para prever o risco de vencimento
    
    caracteristicas = ['dias_em_estoque', 'unidades_vendidas_90dias', 'estoque_atual', 'vida_util_estimada',
                       'preco', 'eh_sazonal', 'cd_subsecao', 'cd_loja']

    # Garantir tipos corretos
    dados['cd_loja'] = dados['cd_loja'].astype(str).astype('category').cat.codes
    dados['cd_subsecao'] = dados['cd_subsecao'].astype(int)

    X = dados[caracteristicas]
    y = dados['vai_vencer']

    # Configurar validação cruzada
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)

    # Criar modelo XGBoost
    modelo = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        random_state=42
    )

    # Realizar validação cruzada
    cv_scores = cross_val_score(modelo, X, y, cv=kfold, scoring='f1')
    print(f"Scores de validação cruzada (F1): {cv_scores}")
    print(f"Média F1 da validação cruzada: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Divisão para teste
    X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)

    # Treinar modelo com todo o conjunto de treinamento
    modelo.fit(X_treino, y_treino)

    return modelo, X_teste, y_teste
