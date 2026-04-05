# Checklist Anti-Data Leakage

| Coluna              | Ação        | Motivo                          |
|---------------------|------------|---------------------------------|
| future_info         | Removida    | Informação do futuro             |
| resolved_time       | Removida    | Só disponível após o evento      |
| manual_label        | Removida    | Inserção humana posterior        |

## Observação
Todas as colunas foram analisadas para garantir que não influenciem indevidamente o modelo.