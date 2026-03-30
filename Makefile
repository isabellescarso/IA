.PHONY: up down app download-data configure-minio upload-minio ingest-data

# ── variáveis ──────────────────────────────────────────────────────────────────
include .env

DATA_SOURCE_URL  := https://physionet.org/files/cgmacros/1.0.0/
DATA_BRONZE_PATH := src/data/bronze
MINIO_ALIAS      := local
MINIO_BUCKET     := cgmacros
MINIO_ENDPOINT   := http://localhost:9000

# ── infra ──────────────────────────────────────────────────────────────────────
up:
	docker compose up -d

down:
	docker compose down

app:
	uvicorn src.api.main:app --reload

run: up app

# ── data ──────────────────────────────────────────────────────────────────────
download-data:
	mkdir -p $(DATA_BRONZE_PATH)
	wget -r -N -c -np $(DATA_SOURCE_URL) -P $(DATA_BRONZE_PATH)

configure-minio:
	mc alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $(MINIO_USER) $(MINIO_PASSWORD)
	mc mb --ignore-existing $(MINIO_ALIAS)/$(MINIO_BUCKET)

extract-data:
	find $(DATA_BRONZE_PATH) -name "*.zip" -exec 7z x {} -o$(DATA_BRONZE_PATH) -aoa \;
	find $(DATA_BRONZE_PATH) -name "*.tar.gz" -exec tar -xzf {} -C $(DATA_BRONZE_PATH) \;
	find $(DATA_BRONZE_PATH) -name "*.gz" ! -name "*.tar.gz" -exec gunzip -k {} \;

upload-minio: configure-minio
	mc cp --recursive $(DATA_BRONZE_PATH)/ $(MINIO_ALIAS)/$(MINIO_BUCKET)/bronze/

ingest-data: download-data extract-data upload-minio