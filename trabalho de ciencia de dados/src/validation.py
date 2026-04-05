import pandas as pd

def validar_dados(df):
    problemas = {}

    # nulos
    problemas['nulos'] = df.isnull().sum().to_dict()

    # duplicados
    problemas['duplicados'] = int(df.duplicated().sum())

    # tipos
    problemas['tipos'] = df.dtypes.astype(str).to_dict()

    return problemas