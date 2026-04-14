import pandas as pd
import os
from validation import validar_dados


def processar_silver():
    """
    Camada Prata do pipeline de engenharia de dados.
    Lê os dados da Bronze, aplica transformações e salva o dataset final para ML.
    """

    # ── 1. Leitura dos Parquets da Bronze ─────────────────────────────────────
    df_incidents = pd.read_parquet("data/bronze/incidents/incidents.parquet")
    df_financial = pd.read_parquet("data/bronze/financial/financial.parquet")
    df_market    = pd.read_parquet("data/bronze/market/market.parquet")

    print(f"Incidents: {df_incidents.shape} | Financial: {df_financial.shape} | Market: {df_market.shape}")

    # ── 2. Merge (left join) pela chave incident_id ───────────────────────────
    # Left join porque nem todo incidente tem empresa de capital aberto (market)
    # ou dados financeiros disponíveis — não podemos perder esses registros
    df = df_incidents.merge(df_financial, on="incident_id", how="left", suffixes=("", "_fin"))
    df = df.merge(df_market,    on="incident_id", how="left", suffixes=("", "_mkt"))

    print(f"Após merge: {df.shape}")

    # ── 3. Remoção de duplicatas pela chave principal ─────────────────────────
    # Garante que cada incidente aparece apenas uma vez no dataset
    df = df.drop_duplicates(subset="incident_id")

    # ── 4. Padronização de categorias ─────────────────────────────────────────
    # Transforma para minúsculo e remove espaços extras
    # Evita que "Ransomware", "ransomware" e "RANSOMWARE" sejam valores diferentes
    if 'attack_vector_primary' in df.columns:
        df['attack_vector_primary'] = df['attack_vector_primary'].str.lower().str.strip()

    if 'quality_grade' in df.columns:
        df['quality_grade'] = df['quality_grade'].str.strip().str.capitalize()

    if 'data_type' in df.columns:
        df['data_type'] = df['data_type'].str.lower().str.strip()

    # ── 5. Tratamento de datas e criação de features temporais ────────────────
    # errors='coerce' transforma datas inválidas em NaT em vez de travar o código
    df['incident_date']  = pd.to_datetime(df['incident_date'],  errors='coerce')
    df['discovery_date'] = pd.to_datetime(df['discovery_date'], errors='coerce')

    # Ano e mês do incidente — úteis como features para modelos de ML
    df['incident_ano'] = df['incident_date'].dt.year
    df['incident_mes'] = df['incident_date'].dt.month

    # Dias até a descoberta do ataque — quanto mais dias, maior tende a ser o impacto
    df['dias_ate_descoberta'] = (df['discovery_date'] - df['incident_date']).dt.days

    # ── 6. Criação do label final para Machine Learning ───────────────────────
    # Label binário: 1 = alto impacto (perda direta > $10M), 0 = baixo impacto
    # Usamos direct_loss_usd porque é a perda inicial registrada,
    # sem depender de dados futuros como ransom ou seguro
    if 'direct_loss_usd' in df.columns:
        df['label_alto_impacto'] = (df['direct_loss_usd'] > 10_000_000).astype(int)

    # ── 7. Remoção de colunas com risco de data leakage ───────────────────────
    # Leakage = informação que não estaria disponível no momento da previsão
    # Se deixadas, o modelo aprende a "resposta pronta" e falha em produção
    leakage_cols = [
        # Derivadas do target — representam o resultado final que queremos prever
        'total_loss_usd',
        'total_loss_method',
        'total_loss_lower_bound',
        'total_loss_upper_bound',
        'inflation_adjusted_usd',
        'cpi_index_used',
        # Conhecidas apenas APÓS o incidente ser resolvido
        'ransom_paid_usd',
        'ransom_source',
        'insurance_payout_usd',
        'regulatory_fine_usd',
        'disclosure_date',
        # Métricas de mercado pós-incidente — preços e retornos do futuro
        'price_7d_after',
        'price_30d_after',
        'days_to_price_recovery',
        'car_0_to_30',
        'car_0_to_90',
        'abnormal_return_7d',
        'abnormal_return_30d',
        'post_incident_volatility_30d',
    ]

    colunas_removidas = [c for c in leakage_cols if c in df.columns]
    df = df.drop(columns=colunas_removidas)
    print(f"\nColunas removidas (leakage): {len(colunas_removidas)}")
    print(colunas_removidas)

    # ── 8. Salvamento do dataset final ────────────────────────────────────────
    os.makedirs("data/silver", exist_ok=True)
    df.to_parquet("data/silver/dataset_final.parquet", index=False)

    # ── 9. Confirmações finais ────────────────────────────────────────────────
    print(f"\nDataset final salvo: data/silver/dataset_final.parquet")
    print(f"Shape final: {df.shape}")
    print(f"\nDistribuição do label:")
    print(df['label_alto_impacto'].value_counts())

    # Executa e exibe o resultado da validação
    resultado = validar_dados(df)

    print("\n=== Validação do dataset final ===")
    print(f"Duplicados: {resultado['duplicados']}")
    print("\nRegras automáticas:")
    for regra, passou in resultado['regras'].items():
        icone = "OK" if passou else "FALHA"
        print(f"  [{icone}] {regra}")

    return resultado

if __name__ == "__main__":
    processar_silver()