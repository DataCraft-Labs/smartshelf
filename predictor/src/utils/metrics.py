# src/utils/metrics.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, roc_curve, auc


def avaliar_modelo(modelo, X_teste, y_teste):
    # Avalia o desempenho do modelo usando várias métricas.
    y_pred = modelo.predict(X_teste)

    print("Métricas de Avaliação")
    print("-" * 30)
    print(f"Acurácia:  {accuracy_score(y_teste, y_pred):.2f}")
    print(f"Precisão:  {precision_score(y_teste, y_pred):.2f}")
    print(f"Recall:    {recall_score(y_teste, y_pred):.2f}")
    print(f"F1 Score:  {f1_score(y_teste, y_pred):.2f}")

    print("\nMatriz de Confusão")
    print(confusion_matrix(y_teste, y_pred))

    print("\nRelatório de Classificação")
    print(classification_report(y_teste, y_pred, digits=2))

    # Adicionando análise de importância de features para XGBoost

    feature_importance = modelo.feature_importances_
    features = ['dias_em_estoque', 'unidades_vendidas_90dias', 'estoque_atual', 'vida_util_estimada',
               'preco', 'eh_sazonal', 'cd_subsecao', 'cd_loja']

    importance_df = pd.DataFrame({'Feature': features, 'Importance': feature_importance})
    importance_df = importance_df.sort_values(by='Importance', ascending=False)

    print("\nImportância das Features:")
    print(importance_df)

    # Visualizar importância das features
    plt.figure(figsize=(10, 6))
    plt.barh(importance_df['Feature'], importance_df['Importance'])
    plt.xlabel('Importância')
    plt.ylabel('Feature')
    plt.title('Importância das Features no Modelo XGBoost')
    plt.tight_layout()
    plt.show()

    # Calcular e plotar a curva ROC
    y_scores = modelo.predict_proba(X_teste)[:,1]
    fpr, tpr, thresholds = roc_curve(y_teste, y_scores)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taxa de Falsos Positivos')
    plt.ylabel('Taxa de Verdadeiros Positivos')
    plt.title('Curva ROC - XGBoost com Validação Cruzada')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.show()
