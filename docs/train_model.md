# Sprint 4 — Treinamento de Modelos

## Pipeline

```
Gold (_ML_READY.parquet) → TemporalSplit (80/20) → Treino → MLflow
```

## Preparação dos Dados

- Colunas utilizadas: numéricas do parquet Gold, excluindo `target_glucose` e `Timestamp`
- Colunas descartadas: todas não numéricas (`Meal Type`, caminhos de imagem, etc.)
- Split: temporal — 80% primeiros registros para treino, 20% finais para teste
- Limpeza: linhas com NaN em qualquer coluna numérica removidas antes do split

## Modelos Avaliados

| Modelo | RMSE | MAE | R² |
|--------|------|-----|----|
| **Ridge** | **20.78** | **16.13** | **0.748** |
| Random Forest | 27.34 | 21.71 | 0.565 |
| XGBoost | 28.25 | 23.22 | 0.535 |

Métrica de decisão: RMSE — penaliza picos de glicose, que representam risco clínico real.

## Modelo Selecionado

**Ridge (alpha=1.0)**

Relação entre lags temporais e glicose futura é predominantemente linear. Modelos de árvore
requerem volume maior de amostras por paciente para superar regressão linear neste domínio.

## Rastreamento

Experimento: `Sprint_4_CGMacros`  
Backend: `sqlite:///mlflow.db`  
UI: `http://localhost:5000`

Cada modelo registra: parâmetros, MAE, RMSE, R², importância de features e artefato do modelo.

## Evidências

- `src/scripts/train_model.py`
- `src/mlops/training_tracker.py`
- `mlruns/`
