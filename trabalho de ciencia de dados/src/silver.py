import pandas as pd
from validation import validar_dados

def processar_silver():
    df_incidents = pd.read_parquet("data/bronze/incidents/incidents.parquet")
    df_financial = pd.read_parquet("data/bronze/financial/financial.parquet")
    df_market = pd.read_parquet("data/bronze/market/market.parquet")

    #merge
    df = df_incidents.merge(df_financial, on="incident_id", how="left", suffixes=("", "_fin"))
    df = df.merge(df_market, on="incident_id", how="left", suffixes=("", "_mkt"))

    # limpeza
    df = df.drop_duplicates(subset="incident_id")
    df = df.dropna() #ajustar pra tratar nulos com cuidado, não no dataset inteiro

    # padronizar categorias
    if 'attack_vector_primary' in df.columns:
        df['attack_vector_primary'] = df['attack_vector_primary'].str.lower().str.strip()

    if 'quality_grade' in df.columns:
        df['quality_grade'] = df['quality_grade'].str.strip().str.capitalize()
        

    if 'data_type' in df.columns:
        df['data_type'] = df['data_type'].str.lower().str.strip()

    # exemplo de label 
    if 'direct_loss_usd' in df.columns:
        df['label_alto_impacto'] = (df['direct_loss_usd'] > 10000000).astype(int)

    # salvar
    df.to_parquet("data/silver/dataset_final.parquet", index=False)

    return validar_dados(df)

if __name__ == "__main__":
    processar_silver()