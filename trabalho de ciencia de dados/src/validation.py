import pandas as pd

def validar_dados(df):
    problemas = {}

    # nulos
    problemas['nulos'] = df.isnull().sum().to_dict()

    # duplicados
    problemas['duplicados'] = int(df.duplicated().sum())

    # tipos
    problemas['tipos'] = df.dtypes.astype(str).to_dict()

     # regras automáticas
    problemas['regras'] = {}

    if 'incident_id' in df.columns:
        problemas['regras']['incident_id_sem_nulos'] = int(df['incident_id'].isnull().sum()) == 0

    if 'quality_grade' in df.columns:
        validos = ['Gold', 'Silver', 'Bronze']
        problemas['regras']['quality_grade_valido'] = df['quality_grade'].dropna().isin(validos).all()

    return problemas