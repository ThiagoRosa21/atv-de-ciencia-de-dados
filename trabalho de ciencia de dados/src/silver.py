import pandas as pd
from validation import validar_dados

def processar_silver():
    df_incidents = pd.read_parquet("data/bronze/incidents/incidents.parquet")
    df_financial = pd.read_parquet("data/bronze/financial/financial.parquet")
    df_market = pd.read_parquet("data/bronze/market/market.parquet")

    # exemplo de merge (ajuste conforme colunas reais)
    df = df_incidents.copy()

    # limpeza
    df = df.drop_duplicates()
    df = df.dropna()

    # exemplo de label (ajuste conforme dataset)
    if 'financial_loss' in df.columns:
        df['label'] = df['financial_loss'].apply(lambda x: 1 if x > 10000 else 0)

    # salvar
    df.to_parquet("data/silver/dataset_final/dataset.parquet", index=False)

    return validar_dados(df)

if __name__ == "__main__":
    processar_silver()