# Camada Gold — Documentação

## Estrutura de Arquivos

```
gold/
├── CGMacros/
│   └── {pid}/
│       └── {pid}_ML_READY.parquet
└── metadata/
    └── {pid}/
        ├── {pid}_stats_summary.csv
        └── {pid}_validation_gold.png
```

---

## CGMacros/{pid}/{pid}_ML_READY.parquet

Dado principal da camada Gold. Produzido a partir da Silver com feature engineering
aplicado para predição de glicose com horizonte de 30 minutos.

**Origem:** `silver/CGMacros/{pid}/{pid}.parquet`  
**Formato:** Parquet, sem índice (`index=False`)

### Colunas adicionadas em relação à Silver

| Coluna | Descrição |
|--------|-----------|
| `Meal_Event` | Flag binária: 1 se há registro de refeição no instante |
| `In_Meal_Window` | Flag: 1 se dentro de janela de 120 min após refeição |
| `target_glucose` | Glicose Libre GL 30 minutos à frente (variável alvo) |
| `lag_GL_5min` | Glicose 5 min atrás |
| `lag_GL_15min` | Glicose 15 min atrás |
| `lag_GL_30min` | Glicose 30 min atrás |
| `lag_GL_60min` | Glicose 60 min atrás |
| `lag_HR_5min` | Frequência cardíaca 5 min atrás |
| `lag_HR_15min` | Frequência cardíaca 15 min atrás |
| `lag_HR_30min` | Frequência cardíaca 30 min atrás |
| `lag_HR_60min` | Frequência cardíaca 60 min atrás |
| `diff_5min` | Variação de glicose nos últimos 5 min |
| `diff_10min` | Variação de glicose nos últimos 10 min |
| `hour` | Hora do dia extraída do Timestamp |
| `hour_sin` | Codificação cíclica senoidal da hora |
| `hour_cos` | Codificação cíclica cossenoidal da hora |

**Linhas removidas:** primeiras 60 (lags) e últimas 30 (target indisponível).

---

## metadata/{pid}/{pid}_stats_summary.csv

Estatísticas descritivas do arquivo ML_READY correspondente.

**Gerado por:** `df.describe().rename_axis('statistic')`  
**Formato:** CSV com coluna-índice nomeada `statistic`

| Coluna | Descrição |
|--------|-----------|
| `statistic` | Métrica: count, mean, min, 25%, 50%, 75%, max, std |
| demais colunas | Uma coluna por feature numérica do parquet |

---

## metadata/{pid}/{pid}_validation_gold.png

Gráfico de validação visual das features geradas.

**Recorte plotado:** linhas 500–1000 do dataset ordenado por Timestamp.

| Elemento | Descrição |
|----------|-----------|
| Linha azul | Glicose atual — `Libre GL` no instante `t` |
| Linha vermelha tracejada | Alvo — `target_glucose` em `t + 30min` |
| Faixa laranja | Janela pós-prandial (`In_Meal_Window == 1`) |

---

## Observações

- Todos os arquivos são gerados por paciente (`pid`), mantendo isolamento de dados.
- O intervalo temporal dos dados é de 1 minuto por registro.
- A janela pós-prandial cobre 120 registros = 2 horas após evento de refeição.
