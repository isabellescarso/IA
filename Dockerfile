FROM python:3.13-slim

WORKDIR /app

# Copia dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY src/ ./src/

# Copia o .env se existir
COPY .env* ./

# Variável de ambiente para o Python encontrar os módulos
ENV PYTHONPATH=/app/src

# Porta padrão (sobrescrita pelo comando no compose)
EXPOSE 8000 7860