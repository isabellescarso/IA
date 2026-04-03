.PHONY: up down app run download-data extract-data configure-minio upload-minio ingest-data train clean-data

# ── variáveis ──────────────────────────────────────────────────────────────────
include .env

DATA_SOURCE_URL   := https://physionet.org/files/cgmacros/1.0.0/
DATA_RAW_PATH     := src/data/raw
MINIO_ALIAS       := local
MINIO_BUCKET      := cgmacros
MINIO_ENDPOINT    := http://localhost:9000
MINIO_BRONZE_PATH := bronze/CGMacros_csv

# ── infra ──────────────────────────────────────────────────────────────────────
up:
	docker compose up -d

down:
	docker compose down

app:
	uvicorn src.api.main:app --reload

run: up app

# ── data ───────────────────────────────────────────────────────────────────────
download-data:
	mkdir -p $(DATA_RAW_PATH)
	wget -r -N -c -np $(DATA_SOURCE_URL) -P $(DATA_RAW_PATH)

extract-data:
	find $(DATA_RAW_PATH) -name "*.zip" -exec 7z x {} -o$(DATA_RAW_PATH) -aoa \;
	find $(DATA_RAW_PATH) -name "*.tar.gz" -exec tar -xzf {} -C $(DATA_RAW_PATH) \;
	find $(DATA_RAW_PATH) -name "*.gz" ! -name "*.tar.gz" -exec gunzip -k {} \;

configure-minio:
	mc alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $(MINIO_USER) $(MINIO_PASSWORD)
	mc mb --ignore-existing $(MINIO_ALIAS)/$(MINIO_BUCKET)

upload-minio: configure-minio
	mc cp --recursive $(DATA_RAW_PATH)/ $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(MINIO_BRONZE_PATH)/

ingest-data: download-data extract-data upload-minio

train:
	python scripts/train_model.py

clean-data:
	rm -rf $(DATA_RAW_PATH)