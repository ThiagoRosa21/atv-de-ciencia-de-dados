import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split



def processar_gold():
    """
    Camada Ouro do pipeline de engenharia de dados.
    Lê os dados da Prata, aplica pré-processamento completo para ML
    e salva os datasets de treino e teste em Parquet.
    """

    # ── 1. Leitura do dataset da Prata ────────────────────────────────────────
    df = pd.read_parquet("data/silver/dataset_final.parquet")
    print(f"Dataset Prata carregado: {df.shape[0]} linhas × {df.shape[1]} colunas")

    # ── 2. Remoção de colunas (anti-leakage + metadados) ─────────────────────
    colunas_remover = [
        'incident_id',
        'company_name',
        'stock_ticker',
        'stock_ticker_mkt',
        'data_source_primary',
        'data_source_secondary',
        'notes',
        'notes_fin',
        'notes_mkt',
        'created_at',
        'updated_at',
        'created_at_fin',
        'updated_at_fin',
        'created_at_mkt',
        'updated_at_mkt',
        'incident_date',
        'incident_date_estimated',
        'discovery_date',
        'review_flag',
        'direct_loss_usd',
    ]

    colunas_remover = [c for c in colunas_remover if c in df.columns]
    df_gold = df.drop(columns=colunas_remover)

    print(f"Colunas removidas (anti-leakage + metadados): {len(colunas_remover)}")
    print(f"Shape após remoção: {df_gold.shape}")

    # ── 3. Separar target e dividir treino/teste ──────────────────────────────
    TARGET = 'label_alto_impacto'
    y = df_gold[TARGET].copy()
    X = df_gold.drop(columns=[TARGET]).copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nDivisão treino/teste:")
    print(f"  Treino: {X_train.shape[0]} linhas | {y_train.mean():.1%} alto impacto")
    print(f"  Teste:  {X_test.shape[0]} linhas | {y_test.mean():.1%} alto impacto")

    # ── 4. Identificar tipos de colunas ──────────────────────────────────────
    colunas_numericas   = X_train.select_dtypes(include=['number']).columns.tolist()
    colunas_categoricas = X_train.select_dtypes(
        include=['object', 'category', 'bool']).columns.tolist()

    # ── 5. Tratamento de missing values ──────────────────────────────────────
    medianas = X_train[colunas_numericas].median()
    X_train[colunas_numericas] = X_train[colunas_numericas].fillna(medianas)
    X_test[colunas_numericas]  = X_test[colunas_numericas].fillna(medianas)

    modas = X_train[colunas_categoricas].mode().iloc[0]
    X_train[colunas_categoricas] = X_train[colunas_categoricas].fillna(modas)
    X_test[colunas_categoricas]  = X_test[colunas_categoricas].fillna(modas)

    print(f"\nMissing values após imputação:")
    print(f"  Treino: {X_train.isnull().sum().sum()} nulos")
    print(f"  Teste:  {X_test.isnull().sum().sum()} nulos")

    # ── 6. Tratamento de outliers (Winsorização IQR) ──────────────────────────
    limites_outliers = {}
    for col in ['direct_loss_usd', 'dias_ate_descoberta']:
        if col in X_train.columns:
            Q1 = X_train[col].quantile(0.25)
            Q3 = X_train[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            X_train[col] = X_train[col].clip(lower=lower, upper=upper)
            X_test[col]  = X_test[col].clip(lower=lower, upper=upper)
            limites_outliers[col] = (lower, upper)
            print(f"  Outliers [{col}]: limites [{lower:,.0f}, {upper:,.0f}]")

    # ── 7. Encoding ───────────────────────────────────────────────────────────
    colunas_label = ['is_public_company', 'earnings_announcement_within_7d']
    colunas_label = [c for c in colunas_label if c in X_train.columns]

    encoders_label = {}
    for col in colunas_label:
        le = LabelEncoder()
        le.fit(X_train[col].astype(str))
        X_train[col] = le.transform(X_train[col].astype(str))
        X_test[col]  = le.transform(X_test[col].astype(str))
        encoders_label[col] = le

    colunas_ohe = [c for c in [
        'attack_vector_primary', 'attack_vector_secondary',
        'data_source_type', 'quality_grade',
        'country_hq', 'direct_loss_method',
    ] if c in X_train.columns]

    X_train_ohe = pd.get_dummies(X_train[colunas_ohe], prefix=colunas_ohe,
                                  drop_first=False, dtype=int)
    X_test_ohe  = pd.get_dummies(X_test[colunas_ohe],  prefix=colunas_ohe,
                                  drop_first=False, dtype=int)

    X_train_ohe, X_test_ohe = X_train_ohe.align(
        X_test_ohe, join='left', axis=1, fill_value=0)

    X_train = X_train.drop(columns=colunas_ohe)
    X_test  = X_test.drop(columns=colunas_ohe)
    X_train = pd.concat([X_train.reset_index(drop=True),
                          X_train_ohe.reset_index(drop=True)], axis=1)
    X_test  = pd.concat([X_test.reset_index(drop=True),
                          X_test_ohe.reset_index(drop=True)], axis=1)

    sobras = X_train.select_dtypes(include=['object', 'category']).columns.tolist()
    if sobras:
        X_train = X_train.drop(columns=sobras)
        X_test  = X_test.drop(columns=sobras)

    print(f"\nEncoding concluído:")
    print(f"  Label Encoding: {colunas_label}")
    print(f"  One-Hot Encoding: {colunas_ohe}")
    print(f"  Shape — treino: {X_train.shape} | teste: {X_test.shape}")

    # ── 8. Scaling (StandardScaler) ───────────────────────────────────────────
    colunas_escalar = X_train.select_dtypes(include=['number']).columns.tolist()
    scaler = StandardScaler()
    X_train[colunas_escalar] = scaler.fit_transform(X_train[colunas_escalar])
    X_test[colunas_escalar]  = scaler.transform(X_test[colunas_escalar])

    print(f"  StandardScaler aplicado em {len(colunas_escalar)} colunas numéricas")

    # ── 9. Salvar em Parquet ──────────────────────────────────────────────────
    os.makedirs("data/gold", exist_ok=True)

    df_train_gold = X_train.copy()
    df_train_gold[TARGET] = y_train.values

    df_test_gold = X_test.copy()
    df_test_gold[TARGET] = y_test.values

    df_train_gold.to_parquet("data/gold/train_gold.parquet", index=False)
    df_test_gold.to_parquet("data/gold/test_gold.parquet",   index=False)

    print(f"\nCamada Ouro salva:")
    print(f"  data/gold/train_gold.parquet — {df_train_gold.shape}")
    print(f"  data/gold/test_gold.parquet  — {df_test_gold.shape}")

    # ── 10. Tabela de transformações ──────────────────────────────────────────
    tabela = pd.DataFrame([
        {
            'Etapa': '1 — Remoção (anti-leakage)',
            'Colunas afetadas': str(len(colunas_remover)),
            'Técnica': 'Drop',
            'Justificativa': 'Identificadores, URLs, metadados e colunas com >90% nulos'
        },
        {
            'Etapa': '2a — Missing Numérico',
            'Colunas afetadas': str(len(colunas_numericas)),
            'Técnica': 'Imputação por Mediana (fit no treino)',
            'Justificativa': 'Robusta a outliers; evita que extremos distorçam a imputação'
        },
        {
            'Etapa': '2b — Missing Categórico',
            'Colunas afetadas': str(len(colunas_categoricas)),
            'Técnica': 'Imputação por Moda (fit no treino)',
            'Justificativa': 'Preserva distribuição original das categorias'
        },
        {
            'Etapa': '3 — Outliers',
            'Colunas afetadas': 'direct_loss_usd, dias_ate_descoberta',
            'Técnica': 'Winsorização IQR (fit no treino)',
            'Justificativa': 'Limita extremos sem remover linhas; dataset pequeno (850 linhas)'
        },
        {
            'Etapa': '4a — Encoding (Label)',
            'Colunas afetadas': str(colunas_label),
            'Técnica': 'LabelEncoder (fit no treino)',
            'Justificativa': 'Colunas binárias — 0/1 suficiente, evita dummies desnecessárias'
        },
        {
            'Etapa': '4b — Encoding (OHE)',
            'Colunas afetadas': str(colunas_ohe),
            'Técnica': 'One-Hot Encoding (fit no treino)',
            'Justificativa': 'Colunas nominais sem ordem — evita que modelo assuma ordinalidade'
        },
        {
            'Etapa': '5 — Scaling',
            'Colunas afetadas': f'{len(colunas_escalar)} colunas numéricas',
            'Técnica': 'StandardScaler (fit no treino)',
            'Justificativa': 'Dataset ML-Ready para qualquer algoritmo'
        },
    ])

    os.makedirs("data/gold", exist_ok=True)
    tabela.to_csv("data/gold/tabela_transformacoes.csv", index=False)

    return {
        'X_train': X_train,
        'X_test':  X_test,
        'y_train': y_train,
        'y_test':  y_test,
        'tabela_transformacoes': tabela,
        'scaler': scaler,
        'limites_outliers': limites_outliers,
    }


def carregar_gold():
    """
    Executa a camada Gold e retorna os dados de treino e teste prontos para ML.
    """
    resultado = processar_gold()

    X_train = resultado['X_train']
    X_test  = resultado['X_test']
    y_train = resultado['y_train']
    y_test  = resultado['y_test']

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    processar_gold()