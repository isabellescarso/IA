.PHONY: up down api ui mlflow validate pipeline \
        ingest-bronze ingest-silver ingest-gold eda embeddings train evaluate-prompts \
        download-data configure-minio extract-data upload-minio ingest-data

# ── variáveis ──────────────────────────────────────────────────────────────────
include .env

DATA_SOURCE_URL  := https://physionet.org/files/cgmacros/1.0.0/
DATA_BRONZE_PATH := src/data/bronze
MINIO_ALIAS      := local
MINIO_BUCKET     := cgmacros
MINIO_ENDPOINT   := http://localhost:9000
PYTHONPATH       := PYTHONPATH=src

# ── infra ──────────────────────────────────────────────────────────────────────
up:
	docker compose up -d

down:
	docker compose down

# ── dados brutos ───────────────────────────────────────────────────────────────
download-data:
	mkdir -p $(DATA_BRONZE_PATH)
	wget -r -N -c -np $(DATA_SOURCE_URL) -P $(DATA_BRONZE_PATH)

configure-minio:
	mc alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $(MINIO_USER) $(MINIO_PASSWORD)
	mc mb --ignore-existing $(MINIO_ALIAS)/$(MINIO_BUCKET)

extract-data:
	find $(DATA_BRONZE_PATH) -name "*.zip"    -exec 7z x {} -o$(DATA_BRONZE_PATH) -aoa \;
	find $(DATA_BRONZE_PATH) -name "*.tar.gz" -exec tar -xzf {} -C $(DATA_BRONZE_PATH) \;
	find $(DATA_BRONZE_PATH) -name "*.gz" ! -name "*.tar.gz" -exec gunzip -k {} \;

upload-minio: configure-minio
	mc cp --recursive $(DATA_BRONZE_PATH)/ $(MINIO_ALIAS)/$(MINIO_BUCKET)/bronze/

ingest-data: download-data extract-data upload-minio

# ── pipeline medallion ─────────────────────────────────────────────────────────
ingest-bronze:
	$(PYTHONPATH) uv run -m scripts.ingest.ingest_bronze

ingest-silver:
	$(PYTHONPATH) uv run -m scripts.ingest.ingest_silver

ingest-gold:
	$(PYTHONPATH) uv run -m scripts.ingest.ingest_gold

eda:
	$(PYTHONPATH) uv run -m scripts.eda.eda_bronze

embeddings:
	$(PYTHONPATH) EMBED_WORKERS=10 uv run -m scripts.generate_embeddings

train:
	$(PYTHONPATH) uv run -m scripts.train_model

evaluate-prompts:
	$(PYTHONPATH) uv run -m scripts.evaluate_prompts

pipeline: ingest-bronze ingest-silver ingest-gold eda train embeddings

# ── serviços ───────────────────────────────────────────────────────────────────
api:
	$(PYTHONPATH) uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

ui:
	$(PYTHONPATH) uv run python src/ui/gradio_app.py

mlflow:
	uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# ── validação ─────────────────────────────────────────────────────────────────
validate:
	$(PYTHONPATH) uv run -m scripts.validate_system