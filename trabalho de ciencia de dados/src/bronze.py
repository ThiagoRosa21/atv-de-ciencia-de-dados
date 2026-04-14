import pandas as pd
import hashlib
from datetime import datetime
import os


def gerar_hash(df):
    """
    Gera um hash MD5 do conteúdo do DataFrame.
    Funciona como impressão digital do arquivo —
    se os dados mudarem em uma carga futura, o hash será diferente.
    Isso garante rastreabilidade no data lineage.
    """
    return hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()


def processar_arquivo(caminho_csv, caminho_saida, nome_arquivo):
    """
    Lê um CSV, aplica transformações mínimas e salva em Parquet.
    A Bronze preserva os dados quase brutos — apenas padroniza
    nomes de colunas e tipos básicos, sem alterar conteúdo.
    """

    # Lê o arquivo CSV original
    df = pd.read_csv(caminho_csv)

    # Padroniza nomes de colunas: minúsculo e sem espaços
    # Ex: "Incident Date" → "incident_date"
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Converte colunas de data para o tipo datetime (tipo básico)
    # errors='coerce' transforma datas inválidas em NaT em vez de travar
    for col in df.columns:
        if "date" in col or col in ["created_at", "updated_at"]:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Garante que a pasta de saída existe antes de salvar
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    # Salva em Parquet — preserva tipos de dados e é mais eficiente que CSV
    df.to_parquet(caminho_saida, index=False)

    # Registra metadados da ingestão para rastreabilidade (data lineage)
    metadata = {
        "arquivo": nome_arquivo,
        "linhas": len(df),
        "hash": gerar_hash(df),
        "data_carga": datetime.now()
    }

    return metadata


def executar_bronze():
    """
    Executa a camada Bronze para os 3 datasets do projeto.
    Lê os CSVs originais, processa cada um e registra o log de ingestão.
    """
    logs = []

    # Lista de arquivos: (origem CSV, destino Parquet, nome para o log)
    arquivos = [
        ("data/bronze/incidents/incidents_master.csv",  "data/bronze/incidents/incidents.parquet",  "incidents"),
        ("data/bronze/financial/financial_impact.csv",  "data/bronze/financial/financial.parquet",  "financial"),
        ("data/bronze/market/market_impact.csv",        "data/bronze/market/market.parquet",        "market"),
    ]

    for entrada, saida, nome in arquivos:
        if os.path.exists(entrada):
            log = processar_arquivo(entrada, saida, nome)
            logs.append(log)
            # Confirmação visual de cada arquivo processado
            print(f"[Bronze] {nome} | {log['linhas']} linhas | hash: {log['hash'][:8]}...")
        else:
            print(f"[Bronze] ARQUIVO NAO ENCONTRADO: {entrada}")

    # Garante que a pasta metadata existe e salva o log de ingestão
    os.makedirs("metadata", exist_ok=True)
    pd.DataFrame(logs).to_csv("metadata/ingestion_log.csv", mode="a", index=False)

    print("\nCamada Bronze executada com sucesso.")


if __name__ == "__main__":
    executar_bronze()