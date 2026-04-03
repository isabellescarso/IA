import os
from io import BytesIO

import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from dotenv import load_dotenv
from minio import Minio

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# =========================
# CARREGAR .ENV
# =========================
load_dotenv()


# =========================
# CONFIGURAÇÕES
# =========================
TARGET = "Dexcom GL"
TEST_SIZE = 0.2
RANDOM_STATE = 42

N_ESTIMATORS = 100
MAX_DEPTH = 15
MIN_SAMPLES_SPLIT = 5
MIN_SAMPLES_LEAF = 2

# Bucket e caminhos no MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_USER = os.getenv("MINIO_USER")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cgmacros")

BRONZE_PREFIX = os.getenv("BRONZE_PREFIX", "bronze/")
SILVER_OBJECT = os.getenv("SILVER_OBJECT", "silver/cgmacros_tratado.csv")
GOLD_OBJECT = os.getenv("GOLD_OBJECT", "gold/dataset_ml.csv")

# MLflow
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("Sprint_4_CGMacros")


# =========================
# VALIDAÇÕES INICIAIS
# =========================
if not MINIO_USER or not MINIO_PASSWORD:
    raise ValueError("MINIO_USER e MINIO_PASSWORD não foram encontrados no .env.")


# =========================
# CONEXÃO COM MINIO
# =========================
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
)

if not client.bucket_exists(MINIO_BUCKET):
    raise ValueError(f"O bucket '{MINIO_BUCKET}' não existe no MinIO.")


# =========================
# FUNÇÕES AUXILIARES
# =========================
def upload_dataframe_to_minio(df: pd.DataFrame, bucket: str, object_name: str):
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=csv_buffer,
        length=csv_buffer.getbuffer().nbytes,
        content_type="text/csv"
    )
    print(f"Arquivo salvo no MinIO: {bucket}/{object_name}")


def read_csv_from_minio(bucket: str, object_name: str) -> pd.DataFrame:
    response = None
    try:
        response = client.get_object(bucket, object_name)
        data = response.read()
        return pd.read_csv(BytesIO(data))
    finally:
        if response is not None:
            response.close()
            response.release_conn()


# =========================
# ETAPA 1 - LER BRONZE
# =========================
dfs = []
arquivos_lidos = []

objetos = client.list_objects(MINIO_BUCKET, prefix=BRONZE_PREFIX, recursive=True)

for obj in objetos:
    if obj.object_name.endswith(".csv"):
        response = None
        try:
            response = client.get_object(MINIO_BUCKET, obj.object_name)
            data = response.read()

            df = pd.read_csv(BytesIO(data))
            df["arquivo_origem"] = obj.object_name

            dfs.append(df)
            arquivos_lidos.append(obj.object_name)
            print(f"Arquivo carregado: {obj.object_name}")

        except Exception as e:
            print(f"Erro ao ler {obj.object_name}: {e}")

        finally:
            if response is not None:
                response.close()
                response.release_conn()

if not dfs:
    raise ValueError(
        f"Nenhum arquivo CSV válido foi encontrado em '{MINIO_BUCKET}/{BRONZE_PREFIX}'."
    )

df_bronze = pd.concat(dfs, ignore_index=True)
print(f"Total de arquivos lidos do bronze: {len(arquivos_lidos)}")
print(f"Shape bronze consolidado: {df_bronze.shape}")


# =========================
# ETAPA 2 - GERAR SILVER
# =========================
df_silver = df_bronze.copy()

if TARGET not in df_silver.columns:
    raise ValueError(f"A coluna alvo '{TARGET}' não existe no dataset.")

if "Timestamp" in df_silver.columns:
    df_silver["Timestamp"] = pd.to_datetime(df_silver["Timestamp"], errors="coerce")
    df_silver["Hora"] = df_silver["Timestamp"].dt.hour
    df_silver["Minuto"] = df_silver["Timestamp"].dt.minute
    df_silver["Dia_Semana"] = df_silver["Timestamp"].dt.dayofweek
    df_silver["Mes"] = df_silver["Timestamp"].dt.month

    df_silver["Hora_sin"] = np.sin(2 * np.pi * df_silver["Hora"] / 24)
    df_silver["Hora_cos"] = np.cos(2 * np.pi * df_silver["Hora"] / 24)

colunas_remover = ["Image path", "Timestamp", "arquivo_origem"]

for col in ["Meal", "Meal_Type", "Diet"]:
    if col in df_silver.columns:
        colunas_remover.append(col)

df_silver = df_silver.drop(columns=colunas_remover, errors="ignore")
df_silver = df_silver.dropna(subset=[TARGET])

# salva silver
upload_dataframe_to_minio(df_silver, MINIO_BUCKET, SILVER_OBJECT)


# =========================
# ETAPA 3 - GERAR GOLD
# =========================
df_gold = df_silver.copy()

# manter apenas colunas numéricas
df_gold = df_gold.select_dtypes(include=["number"])

# preencher faltantes
df_gold = df_gold.interpolate(method="linear", limit_direction="both")
df_gold = df_gold.fillna(0)

if TARGET not in df_gold.columns:
    raise ValueError(f"A coluna alvo '{TARGET}' não existe após gerar o gold.")

# salva gold
upload_dataframe_to_minio(df_gold, MINIO_BUCKET, GOLD_OBJECT)


# =========================
# ETAPA 4 - LER GOLD E TREINAR
# =========================
df_train = read_csv_from_minio(MINIO_BUCKET, GOLD_OBJECT)

X = df_train.drop(TARGET, axis=1)
y = df_train[TARGET]

if X.empty:
    raise ValueError("Após o pré-processamento, não sobraram colunas para treino.")

print(f"Shape final de X: {X.shape}")
print(f"Shape final de y: {y.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE
)


# =========================
# ETAPA 5 - TREINAMENTO + MLFLOW
# =========================
with mlflow.start_run(run_name="random_forest_medallion"):
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

    mlflow.log_param("target", TARGET)
    mlflow.log_param("test_size", TEST_SIZE)
    mlflow.log_param("random_state", RANDOM_STATE)
    mlflow.log_param("n_estimators", N_ESTIMATORS)
    mlflow.log_param("max_depth", MAX_DEPTH)
    mlflow.log_param("min_samples_split", MIN_SAMPLES_SPLIT)
    mlflow.log_param("min_samples_leaf", MIN_SAMPLES_LEAF)

    mlflow.log_param("bucket", MINIO_BUCKET)
    mlflow.log_param("bronze_prefix", BRONZE_PREFIX)
    mlflow.log_param("silver_object", SILVER_OBJECT)
    mlflow.log_param("gold_object", GOLD_OBJECT)

    mlflow.log_param("qtd_arquivos_lidos", len(arquivos_lidos))
    mlflow.log_param("qtd_linhas_gold", len(df_gold))
    mlflow.log_param("qtd_features", X.shape[1])

    mlflow.log_metric("MAE", mae)
    mlflow.log_metric("R2", r2)

    mlflow.sklearn.log_model(model, "modelo_glicose")

print("Pipeline bronze > silver > gold > treino finalizado com sucesso.")