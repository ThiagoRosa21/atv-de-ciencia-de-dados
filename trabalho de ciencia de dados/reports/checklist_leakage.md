# Checklist Anti-Data Leakage

Colunas analisadas e removidas por representarem informações indisponíveis no momento real da previsão.

## Colunas Removidas

| Coluna | Dataset | Motivo |
|---|---|---|
| `total_loss_usd` | financial | Resultado final do impacto — derivada do target |
| `total_loss_method` | financial | Descreve como o total foi calculado — derivada do target |
| `total_loss_lower_bound` | financial | Faixa inferior do total — derivada do target |
| `total_loss_upper_bound` | financial | Faixa superior do total — derivada do target |
| `inflation_adjusted_usd` | financial | Ajuste sobre total_loss_usd — derivada do target |
| `cpi_index_used` | financial | Índice auxiliar do cálculo do total_loss |
| `ransom_paid_usd` | financial | Valor pago após negociação com atacante — disponível no futuro |
| `ransom_source` | financial | Fonte do pagamento do resgate — disponível no futuro |
| `insurance_payout_usd` | financial | Pagamento do seguro — disponível semanas depois |
| `regulatory_fine_usd` | financial | Multa regulatória — aplicada meses depois |
| `disclosure_date` | incidents | Data de divulgação pública — posterior ao incidente |
| `price_7d_after` | market | Preço da ação 7 dias após o incidente — futuro |
| `price_30d_after` | market | Preço da ação 30 dias após o incidente — futuro |
| `days_to_price_recovery` | market | Dias até recuperação do preço — futuro |
| `car_0_to_30` | market | Retorno acumulado 0–30 dias — futuro |
| `car_0_to_90` | market | Retorno acumulado 0–90 dias — futuro |
| `abnormal_return_7d` | market | Retorno anormal em 7 dias — futuro |
| `abnormal_return_30d` | market | Retorno anormal em 30 dias — futuro |
| `post_incident_volatility_30d` | market | Volatilidade pós-incidente — futuro |

## O que é Data Leakage

Data leakage acontece quando o modelo recebe durante o treino informações que não estariam disponíveis no momento real da previsão. Isso gera performance artificial no treino mas causa falha em produção.

As colunas removidas foram divididas em dois grupos:

- **Derivadas do target**: representam o resultado final que queremos prever — se deixadas, o modelo aprende a resposta pronta
- **Informações do futuro**: só ficam disponíveis dias ou meses após o incidente — impossível tê-las no momento da previsão

## Resultado

Total de colunas removidas: **19**
Dataset final aprovado sem risco de data leakage.
