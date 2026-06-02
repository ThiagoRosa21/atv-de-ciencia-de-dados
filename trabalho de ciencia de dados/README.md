# Pipeline de Dados — Cibersegurança (ML-Ready)

## Objetivo
Construir um pipeline de dados completo com as camadas Bronze, Silver e Gold para classificação de incidentes de cibersegurança de alto impacto financeiro, seguindo a arquitetura Medallion.

## Arquitetura
CSV Brutos → Bronze → Silver → Gold → Modelo ML

## Estrutura das Camadas

| Camada | Arquivo | Descrição |
|--------|---------|-----------|
| Bronze | `src/bronze.py` | Ingestão, padronização de colunas, hash MD5, log de metadados |
| Silver | `src/silver.py` | Merge das 3 fontes, limpeza, features temporais, anti-leakage, label |
| Gold | `src/gold.py` | Imputação, outliers, encoding, scaling, split treino/teste |

## Estrutura de Pastas
trabalho de ciencia de dados/
├── data/
│   ├── bronze/
│   │   ├── incidents/incidents.parquet
│   │   ├── financial/financial.parquet
│   │   └── market/market.parquet
│   ├── silver/
│   │   ├── dataset_final.parquet
│   │   └── graficos EDA (*.png)
│   └── gold/
│       ├── train_gold.parquet
│       ├── test_gold.parquet
│       └── tabela_transformacoes.csv
├── metadata/
│   └── ingestion_log.csv
├── notebooks/
│   └── pipeline.ipynb
├── reports/
│   ├── checklist_leakage.md
│   ├── data_quality.md
│   └── reconciliacao_final.json
└── src/
    ├── bronze.py
    ├── silver.py
    ├── gold.py
    └── validation.py

## Tecnologias
- Python 3.12
- Pandas / NumPy
- PyArrow (Parquet)
- Scikit-learn
- Matplotlib / Seaborn

## Dataset
- 850 incidentes de cibersegurança
- 3 fontes: incidents (850), financial (778), market (358)
- Label: `label_alto_impacto` — 1 se perda direta acima de $10M
- Silver: 850 linhas × 65 colunas
- Gold treino: 680 linhas × 97 features
- Gold teste: 170 linhas × 97 features
- Balanceamento: 41.2% alto impacto (treino e teste iguais)

## Anti-Leakage

| Coluna | Motivo |
|--------|--------|
| `direct_loss_usd` | Base do label — vazamento direto |
| `total_loss_usd` e derivadas | Resultado final do incidente |
| `ransom_paid_usd` | Conhecido apenas após resolução |
| `insurance_payout_usd` | Conhecido apenas após resolução |
| `price_7d_after`, `price_30d_after` | Preços futuros pós-incidente |
| `days_to_price_recovery` | Métrica pós-incidente |

## Resultados do Modelo

| Métrica | Valor |
|---------|-------|
| Algoritmo | DecisionTreeClassifier |
| Profundidade máxima | 5 |
| Acurácia | 91.8% |
| Precisão | 90.0% |
| Recall | 90.0% |
| F1-Score | 90.0% |

## Reconciliação Final

| Validação | Status |
|-----------|--------|
| Treino + Teste == Silver (850) | ✅ |
| Silver preserva grão de incidents | ✅ |
| Target ausente no X_train | ✅ |
| direct_loss_usd removido do X_train | ✅ |

## Como Executar
pip install pandas pyarrow matplotlib seaborn scikit-learn numpy
python src/bronze.py
python src/silver.py
python src/gold.py
jupyter notebook notebooks/pipeline.ipynb

## Execução do Notebook
O notebook pipeline.ipynb executa todas as etapas em sequência:
1. Seção 0 — Imports e configuração
2. Seção 1 — Camada Bronze
3. Seção 2 — Qualidade dos dados Bronze
4. Seção 3 — Camada Silver
5. Seção 4 — Resumo do pipeline
6. Seção 5 — EDA por hipóteses (3 hipóteses, 7 gráficos)
7. Seção 6 — Camada Gold + Modelo (Árvore de Decisão)
8. Seção 7 — Reconciliação final