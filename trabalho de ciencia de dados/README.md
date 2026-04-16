# Pipeline de Dados — Cibersegurança

## Objetivo
Construir um pipeline de dados com camadas Bronze e Prata para preparação de dados de incidentes de cibersegurança para Machine Learning.

## Estrutura
- **Bronze**: dados brutos preservados em Parquet com registro de metadados e hash MD5
- **Prata**: dados limpos, transformados e prontos para modelos preditivos

## Tecnologias
- Python
- Pandas
- PyArrow (Parquet)
- Matplotlib / Seaborn

## Dataset
- 850 incidentes de cibersegurança
- 3 fontes: incidents, financial, market
- Label: `label_alto_impacto` — 1 se perda direta acima de $10M
- Dataset final: 850 linhas × 65 colunas

## Execução

```bash
pip install pandas pyarrow matplotlib seaborn

python src/bronze.py
python src/silver.py
jupyter notebook notebooks/pipeline.ipynb
