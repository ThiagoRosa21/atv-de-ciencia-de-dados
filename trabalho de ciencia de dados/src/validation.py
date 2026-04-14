import pandas as pd


def validar_dados(df):
    """
    Valida um DataFrame com regras automáticas e critérios claros.
    Retorna um dicionário com os resultados de cada verificação.
    """
    problemas = {}

    # ── 1. Nulos por coluna ───────────────────────────────────────────────────
    # Conta quantos valores estão faltando em cada coluna
    problemas['nulos'] = df.isnull().sum().to_dict()

    # ── 2. Duplicatas totais ──────────────────────────────────────────────────
    # Verifica se há linhas completamente iguais no dataset
    problemas['duplicados'] = int(df.duplicated().sum())

    # ── 3. Tipos de cada coluna ───────────────────────────────────────────────
    # Mostra o tipo de dado detectado (int, float, object, datetime...)
    problemas['tipos'] = df.dtypes.astype(str).to_dict()

    # ── 4. Regras automáticas com critérios claros ────────────────────────────
    # Cada regra retorna True (passou) ou False (falhou)
    problemas['regras'] = {}

    # Regra 1: incident_id não pode ter nenhum nulo
    # É a chave principal — sem ela não conseguimos identificar o incidente
    if 'incident_id' in df.columns:
        problemas['regras']['incident_id_sem_nulos'] = (
            int(df['incident_id'].isnull().sum()) == 0
        )

    # Regra 2: quality_grade deve ser somente Gold, Silver ou Bronze
    # Qualquer outro valor indica inconsistência na entrada de dados
    if 'quality_grade' in df.columns:
        validos = ['Gold', 'Silver', 'Bronze']
        problemas['regras']['quality_grade_valido'] = bool(
            df['quality_grade'].dropna().isin(validos).all()
        )

    # Regra 3: attack_vector_primary não pode ter mais de 20% de nulos
    # É a coluna principal de classificação do ataque — muitos nulos
    # comprometem qualquer análise ou modelo treinado sobre esses dados
    if 'attack_vector_primary' in df.columns:
        pct_nulos = df['attack_vector_primary'].isnull().mean() * 100
        problemas['regras']['attack_vector_nulos_aceitaveis'] = pct_nulos <= 20

    # Regra 4: attribution_confidence deve estar no conjunto esperado
    # O dataset usa valores controlados — qualquer outro é erro de entrada
    if 'attribution_confidence' in df.columns:
        validos_conf = ['confirmed', 'probable', 'suspected', 'unknown']
        problemas['regras']['attribution_confidence_valido'] = bool(
            df['attribution_confidence'].dropna().isin(validos_conf).all()
        )

    # Regra 5: direct_loss_usd não pode ter valores negativos
    # Perda financeira negativa não faz sentido — seria erro de registro
    if 'direct_loss_usd' in df.columns:
        problemas['regras']['direct_loss_sem_negativos'] = bool(
            (df['direct_loss_usd'].dropna() >= 0).all()
        )

    return problemas