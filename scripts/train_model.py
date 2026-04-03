import os
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# =========================
# CONFIGURAÇÕES
# =========================
CAMINHO_DADOS = r"C:\Users\josec\OneDrive\Desktop\teste\CGMacros_dateshifted365\CGMacros"
TARGET = "Dexcom GL"
TEST_SIZE = 0.2
RANDOM_STATE = 42

N_ESTIMATORS = 100
MAX_DEPTH = 15
MIN_SAMPLES_SPLIT = 5
MIN_SAMPLES_LEAF = 2

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("Sprint_4_CGMacros")


# =========================
# LEITURA DOS DADOS
# =========================
dfs = []

if not os.path.exists(CAMINHO_DADOS):
    raise FileNotFoundError(f"Caminho não encontrado: {CAMINHO_DADOS}")

for pasta in os.listdir(CAMINHO_DADOS):
    pasta_path = os.path.join(CAMINHO_DADOS, pasta)

    if os.path.isdir(pasta_path):
        arquivo = os.path.join(pasta_path, f"{pasta}.csv")

        if os.path.exists(arquivo):
            df = pd.read_csv(arquivo)
            df["paciente"] = pasta
            dfs.append(df)

if not dfs:
    raise ValueError("Nenhum arquivo CSV válido foi encontrado.")

df_final = pd.concat(dfs, ignore_index=True)


# =========================
# PRÉ-PROCESSAMENTO
# =========================
if TARGET not in df_final.columns:
    raise ValueError(f"A coluna alvo '{TARGET}' não existe no dataset.")

if "Timestamp" in df_final.columns:
    df_final["Timestamp"] = pd.to_datetime(df_final["Timestamp"], errors="coerce")
    df_final["Hora"] = df_final["Timestamp"].dt.hour
    df_final["Minuto"] = df_final["Timestamp"].dt.minute
    df_final["Dia_Semana"] = df_final["Timestamp"].dt.dayofweek
    df_final["Mes"] = df_final["Timestamp"].dt.month

    # features cíclicas de hora
    df_final["Hora_sin"] = np.sin(2 * np.pi * df_final["Hora"] / 24)
    df_final["Hora_cos"] = np.cos(2 * np.pi * df_final["Hora"] / 24)

colunas_remover = ["Image path", "Timestamp", "paciente"]

for col in ["Meal", "Meal_Type", "Diet"]:
    if col in df_final.columns:
        colunas_remover.append(col)

df_final = df_final.drop(columns=colunas_remover, errors="ignore")
df_final = df_final.dropna(subset=[TARGET])

# mantém apenas colunas numéricas
df_final = df_final.select_dtypes(include=["number"])

# preenche faltantes
df_final = df_final.interpolate(method="linear", limit_direction="both")
df_final = df_final.fillna(0)

X = df_final.drop(TARGET, axis=1)
y = df_final[TARGET]

if X.empty:
    raise ValueError("Após o pré-processamento, não sobraram colunas para treino.")

print(f"Shape final: {X.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE
)


# =========================
# TREINAMENTO + MLFLOW
# =========================
with mlflow.start_run(run_name="random_forest_melhorado"):
    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        min_samples_split=MIN_SAMPLES_SPLIT,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        n_jobs=-1,
        random_state=RANDOM_STATE
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: {mae:.4f}")
    print(f"R2: {r2:.4f}")

    # parâmetros
    mlflow.log_param("target", TARGET)
    mlflow.log_param("test_size", TEST_SIZE)
    mlflow.log_param("random_state", RANDOM_STATE)
    mlflow.log_param("n_estimators", N_ESTIMATORS)
    mlflow.log_param("max_depth", MAX_DEPTH)
    mlflow.log_param("min_samples_split", MIN_SAMPLES_SPLIT)
    mlflow.log_param("min_samples_leaf", MIN_SAMPLES_LEAF)

    # infos do dataset
    mlflow.log_param("qtd_linhas", len(df_final))
    mlflow.log_param("qtd_features", X.shape[1])

    # métricas
    mlflow.log_metric("MAE", mae)
    mlflow.log_metric("R2", r2)

    # modelo
    mlflow.sklearn.log_model(model, "modelo_glicose")

print("Treinamento finalizado e registrado no MLflow com sucesso.")