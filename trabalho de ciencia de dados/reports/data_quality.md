# Relatório de Qualidade de Dados

## Camada Bronze

### Resumo Geral

| Dataset | Linhas | Colunas | Duplicados |
|---|---|---|---|
| incidents_master.csv | 850 | 32 | 0 |
| financial_impact.csv | 778 | 19 | 0 |
| market_impact.csv | 358 | 31 | 0 |

### Problemas identificados
- Dataset `market_impact` possui apenas 358 registros de 850 incidentes — nem toda empresa envolvida é de capital aberto. Tratado com **left join** para preservar todos os incidentes.
- Colunas com nulos aceitáveis pelo contexto: `attack_vector_secondary`, `attributed_group`, `days_to_price_recovery`.

### Regras automáticas de validação

| Regra | Critério | Resultado |
|---|---|---|
| incident_id_sem_nulos | Nenhum nulo permitido na chave principal | ✅ OK |
| quality_grade_valido | Apenas Gold, Silver ou Bronze | ✅ OK |
| attack_vector_nulos_aceitaveis | Percentual de nulos ≤ 20% | ✅ OK |
| attribution_confidence_valido | Apenas confirmed, probable, suspected, unknown | ✅ OK |
| direct_loss_sem_negativos | Todos os valores ≥ 0 | ✅ OK |

---

## Camada Prata

### Resumo do dataset final

| Métrica | Valor |
|---|---|
| Linhas | 850 |
| Colunas | 65 |
| Duplicados | 0 |
| Colunas de leakage removidas | 19 |

### Tratamentos realizados

| Etapa | Descrição |
|---|---|
| Merge | Left join dos 3 datasets pela chave `incident_id` |
| Deduplicação | Remoção de duplicatas por `incident_id` |
| Padronização | Categorias em minúsculo e sem espaços extras |
| Features temporais | `incident_ano`, `incident_mes`, `dias_ate_descoberta` |
| Label ML | `label_alto_impacto` — 1 se `direct_loss_usd > $10M` |
| Anti-leakage | Remoção de 19 colunas com informação futura |

### Distribuição do label

| Classe | Quantidade | Percentual |
|---|---|---|
| 0 — Baixo impacto (≤ $10M) | 500 | 58,8% |
| 1 — Alto impacto (> $10M) | 350 | 41,2% |

### Resultado
Dataset final aprovado em todas as regras de validação e pronto para uso em modelos preditivos de Machine Learning.
