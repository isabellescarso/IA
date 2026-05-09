#!/usr/bin/env sh
set -e

apk add --no-cache wget p7zip curl

DATA_PATH=/data/bronze
wget -r -N -c -np https://physionet.org/files/cgmacros/1.0.0/ -P "$DATA_PATH"

find "$DATA_PATH" -name "*.zip"    -exec 7z x {} -o"$DATA_PATH" -aoa \;
find "$DATA_PATH" -name "*.tar.gz" -exec tar -xzf {} -C "$DATA_PATH" \;
find "$DATA_PATH" -name "*.gz" ! -name "*.tar.gz" -exec gunzip -k {} \;

wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
chmod +x /usr/local/bin/mc

mc alias set local http://minio:9000 "$MINIO_USER" "$MINIO_PASSWORD"
mc mb --ignore-existing local/cgmacros
mc cp --recursive "$DATA_PATH"/ local/cgmacros/bronze/