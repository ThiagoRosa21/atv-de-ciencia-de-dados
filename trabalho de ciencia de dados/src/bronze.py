import pandas as pd
import hashlib
from datetime import datetime
import os

def gerar_hash(df):
    return hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()

def processar_arquivo(caminho_csv, caminho_saida, nome_arquivo):
    df = pd.read_csv(caminho_csv)

    # padronizar colunas
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # converter tipos básicos de data
    for col in df.columns:
        if "date" in col or col in ["created_at", "updated_at"]:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # garantir que a pasta de saída existe
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    # salvar parquet
    df.to_parquet(caminho_saida, index=False)

    # metadata
    metadata = {
        "arquivo": nome_arquivo,
        "linhas": len(df),
        "hash": gerar_hash(df),
        "data_carga": datetime.now()
    }

    return metadata


def executar_bronze():
    logs = []

    arquivos = [
        ("data/bronze/incidents/incidents_master.csv", "data/bronze/incidents/incidents.parquet", "incidents"),
        ("data/bronze/financial/financial_impact.csv", "data/bronze/financial/financial.parquet", "financial"),
        ("data/bronze/market/market_impact.csv", "data/bronze/market/market.parquet", "market"),
    ]

    for entrada, saida, nome in arquivos:
        if os.path.exists(entrada):
            log = processar_arquivo(entrada, saida, nome)
            logs.append(log)
        else:
            print(f"Arquivo não encontrado: {entrada}")


    os.makedirs("metadata", exist_ok=True)
    pd.DataFrame(logs).to_csv("metadata/ingestion_log.csv", mode='a', index=False)

    print("Camada Bronze executada com sucesso.")

if __name__ == "__main__":
    executar_bronze()