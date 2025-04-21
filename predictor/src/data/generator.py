# src/data/generator.py
import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

def gerar_dados_simulados(seed=42):
    """
    Gera dados simulados que representam uma amostra do estoque da Leroy Merlin.
    """
    np.random.seed(seed)
    random.seed(seed)

    # Seções e subseções com faixa de validade
    secoes = {
        'JARDIM': [('Plantas para Jardim', 14, 60)],
        'PINTURA': [('Centro de cor', 365, 730), ('Adesivos e colas', 180, 365)],
        'FERRAGENS': [('Ferragens de Móveis', 365, 1095)],
        'MATERIAIS': [('Cimento, areia, arg, cascalho', 180, 730)]
    }

    # Nomes realistas por subseção
    nomes_produtos = {
        'Plantas para Jardim': ['Azaleia P17', 'Samambaia Grande', 'Orquídea Branca', 'Lavanda', 'Hortênsia Azul', 'Bromélia', 'Cacto Miniatura', 'Bougainville', 'Palmeira Areca'],
        'Centro de cor': ['Tinta Acrílica Branco Neve', 'Corante Azul Céu', 'Tinta Spray Fosca', 'Esmalte Sintético Preto', 'Tinta Látex Cinza Urbano'],
        'Adesivos e colas': ['Cola Madeira Extra Forte', 'Adesivo Epóxi Transparente', 'Supercola Instantânea', 'Cola PVA Branca 1L', 'Adesivo PU 400g'],
        'Ferragens de Móveis': ['Dobradiça Aço 3"', 'Parafuso Sextavado 5mm', 'Puxador Inox Curvo', 'Trilho Telescópico 35cm', 'Fechadura Magnética'],
        'Cimento, areia, arg, cascalho': ['Saco de Cimento CP II 50kg', 'Areia Média Ensacada', 'Argamassa AC1 20kg', 'Cascalho Lavado', 'Argila Expandida 10L']
    }

    produtos = []
    for _ in range(5000):
        secao = random.choice(list(secoes.keys()))
        subsecao_nome, min_vu, max_vu = random.choice(secoes[secao])
        cd_subsecao = np.random.randint(100, 999)
        nome_produto = random.choice(nomes_produtos[subsecao_nome])

        # Vida útil com ruído controlado
        p_vu = np.random.rand()
        if p_vu < 0.10:
            vida_util = np.random.randint(3, 10)  # Muito curta
        elif p_vu < 0.15:
            vida_util = np.random.randint(max_vu + 1, max_vu + 365)  # Muito longa
        else:
            vida_util = np.random.randint(min_vu, max_vu)

        # Preço com ruído
        preco = round(np.random.uniform(5, 500), 2)
        if np.random.rand() < 0.05:
            preco *= np.random.randint(10, 100)

        produtos.append({
            'LM': np.random.randint(80000000, 99999999),
            'nome_produto': nome_produto,
            'secao': secao,
            'subsecao': subsecao_nome,
            'cd_subsecao': cd_subsecao,
            'vida_util_subsecao': vida_util,
            'preco': preco,
            'eh_sazonal': np.random.choice([0, 1], p=[0.7, 0.3])
        })

    df_produtos = pd.DataFrame(produtos)

    # Lojas fixas
    nomes_lojas = ['NITEROI', 'MORUMBI', 'SOROCABA', 'TAGUATINGA', 'MARGINAL TIETE 2', 'VITORIA', 'RIO NORTE']
    lojas = []
    for i, nome in enumerate(nomes_lojas):
        lojas.append({
            'cd_loja': f"{i:02d}",
            'nome_loja': nome
        })

    # Estoque + vendas + ruído
    registros = []
    for produto in produtos:
        for loja in lojas:
            if np.random.rand() < 0.3:
                # Dias em estoque
                dias_estoque = np.random.randint(0, produto['vida_util_subsecao'] + 50)
                if np.random.rand() < 0.05:  # Estoque muito antigo
                    dias_estoque += 730  # 2 anos

                data_recebimento = pd.Timestamp.now() - pd.Timedelta(days=dias_estoque)
                data_recebimento = data_recebimento.replace(second=0, microsecond=0)

                # Vendas (encalhe com 10% de chance)
                if np.random.rand() < 0.10:
                    unidades_vendidas = 0
                else:
                    velocidade = np.random.exponential(scale=1.0)
                    unidades_vendidas = int(velocidade * 90 * np.random.uniform(0.3, 2.0))

                # Estoque atual com chance de exagero
                estoque = np.random.randint(1, 80)
                if np.random.rand() < 0.05:
                    estoque *= 10

                # Faltantes intencionais
                preco_final = produto['preco'] if np.random.rand() > 0.02 else None
                estoque_final = estoque if np.random.rand() > 0.02 else None

                data_ultima_venda = pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 10))
                data_ultima_venda = data_ultima_venda.replace(second=0, microsecond=0)

                registros.append({
                    'LM': produto['LM'],
                    'nome_produto': produto['nome_produto'],
                    'secao': produto['secao'],
                    'subsecao': produto['subsecao'],
                    'cd_subsecao': produto['cd_subsecao'],
                    'vida_util_subsecao': produto['vida_util_subsecao'],
                    'preco': preco_final,
                    'eh_sazonal': produto['eh_sazonal'],
                    'cd_loja': loja['cd_loja'],
                    'nome_loja': loja['nome_loja'],
                    'estoque_atual': estoque_final,
                    'data_recebimento': data_recebimento.strftime("%Y-%m-%d %H:%M"),
                    'unidades_vendidas_90dias': unidades_vendidas,
                    'data_ultima_venda': data_ultima_venda.strftime("%Y-%m-%d %H:%M")
                })

    df_final = pd.DataFrame(registros)
    return df_final
