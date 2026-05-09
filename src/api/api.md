# Contrato da API — RAG CGMacros

**Versão:** 2.0.0  
**Base URL:** `http://localhost:8000`  
**Documentação interativa:** `http://localhost:8000/docs` (Swagger UI)  
**Framework:** FastAPI

---

## Visão Geral

A API RAG CGMacros expõe endpoints HTTP para consulta ao pipeline de Retrieval-Augmented Generation desenvolvido sobre dados de monitoramento contínuo de glicose (CGMacros). O sistema combina:

- Busca vetorial no **Milvus**
- Predição de glicose via modelo **Ridge** registrado no **MLflow**
- Geração de resposta via **LLM local (Ollama)** — suporta dois modelos: `llama3.2` e `mistral`
- Persistência de logs de consultas no **PostgreSQL**
- Rastreamento de experimentos no **MLflow**

---

## Autenticação

Nenhuma autenticação exigida nesta versão. A API opera em ambiente local isolado via Docker Compose.

---

## Modelos Disponíveis

| Modelo       | Tipo         | Uso recomendado                            |
|--------------|--------------|--------------------------------------------|
| `llama3.2`   | LLM (padrão) | Respostas em português, contexto de saúde  |
| `mistral`    | LLM (alt.)   | Respostas mais concisas e técnicas         |

O modelo pode ser selecionado por chamada via o campo `model` no body do `/ask`.

---

## Endpoints

### 1. `POST /ask`

Realiza uma pergunta ao pipeline RAG. A API recupera contexto vetorial, aplica predição de glicose e gera resposta textual via LLM. O log da consulta é salvo automaticamente no PostgreSQL e rastreado no MLflow.

**Request**

```
POST /ask
Content-Type: application/json
```

**Body**

| Campo      | Tipo            | Obrigatório | Descrição                                                        |
|------------|-----------------|-------------|------------------------------------------------------------------|
| `question` | string          | Sim         | Pergunta em linguagem natural                                    |
| `model`    | string \| null  | Não         | Modelo LLM a usar: `"llama3.2"` ou `"mistral"`. Padrão: `llama3.2` |

**Exemplo de request — modelo padrão**

```json
{
  "question": "Qual o impacto de carboidratos na glicose do paciente CGMacros-012?"
}
```

**Exemplo de request — selecionando o segundo modelo**

```json
{
  "question": "Resuma o padrão glicêmico do paciente CGMacros-039.",
  "model": "mistral"
}
```

**Response — 200 OK**

| Campo        | Tipo   | Descrição                               |
|--------------|--------|-----------------------------------------|
| `answer`     | string | Resposta gerada pelo LLM com contexto   |
| `model_used` | string | Nome do modelo que gerou a resposta     |

**Exemplo de response**

```json
{
  "answer": "Com base nos dados do paciente CGMacros-012, o consumo de carboidratos simples provoca elevação média de glicose de 45 mg/dL em aproximadamente 30 minutos após a refeição...",
  "model_used": "llama3.2"
}
```

**Efeitos colaterais**

- Log salvo na tabela `ask_logs` do PostgreSQL com `question`, `answer`, `model_used` e `latency_ms`.
- Experimento registrado no MLflow com parâmetros e métrica de latência.

**Erros possíveis**

| Código | Descrição                                              |
|--------|--------------------------------------------------------|
| `422`  | Campo `question` ausente ou inválido                   |
| `500`  | Falha interna no pipeline RAG ou no LLM               |
| `503`  | Serviços dependentes indisponíveis (Milvus, Ollama)    |

---

### 2. `GET /metadata`

Retorna metadados do estado atual do sistema: total de vetores no Milvus, pacientes disponíveis e modelos em uso.

**Request**

```
GET /metadata
```

**Response — 200 OK**

| Campo           | Tipo          | Descrição                                   |
|-----------------|---------------|---------------------------------------------|
| `total_vectors` | integer       | Total de embeddings indexados no Milvus     |
| `patients`      | array[string] | IDs dos pacientes com dados disponíveis     |
| `embed_model`   | string        | Modelo de embedding em uso                  |
| `llm_model`     | string        | Modelo LLM padrão em uso                   |

**Exemplo de response**

```json
{
  "total_vectors": 15842,
  "patients": ["CGMacros-012", "CGMacros-039"],
  "embed_model": "nomic-embed-text",
  "llm_model": "llama3.2"
}
```

---

### 3. `GET /health`

Verifica o estado operacional da API.

**Request**

```
GET /health
```

**Response — 200 OK**

```json
{
  "checks": [
    {
      "status": "ok",
      "time": "2026-05-09T10:00:00-03:00",
      "version": "2.0.0"
    }
  ]
}
```

**Response — 503 Service Unavailable**

```json
{
  "detail": "System is degraded"
}
```

---

## Modelos de Dados

### `AskRequest`

```json
{
  "question": "string",
  "model": "string | null"
}
```

### `AskResponse`

```json
{
  "answer": "string",
  "model_used": "string"
}
```

### `MetadataResponse`

```json
{
  "total_vectors": 0,
  "patients": ["string"],
  "embed_model": "string",
  "llm_model": "string"
}
```

### `HealthReport`

```json
{
  "checks": [
    {
      "status": "string",
      "time": "string (ISO 8601)",
      "version": "string"
    }
  ]
}
```

---

## Persistência no PostgreSQL

Toda consulta ao endpoint `/ask` é automaticamente salva na tabela `ask_logs`:

| Coluna       | Tipo        | Descrição                          |
|--------------|-------------|------------------------------------|
| `id`         | SERIAL PK   | Identificador único                |
| `question`   | TEXT        | Pergunta feita pelo usuário        |
| `answer`     | TEXT        | Resposta gerada pelo LLM           |
| `model_used` | VARCHAR(64) | Modelo LLM utilizado               |
| `latency_ms` | INTEGER     | Tempo de resposta em milissegundos |
| `created_at` | TIMESTAMPTZ | Data/hora da consulta              |

---

## Variáveis de Ambiente

| Variável              | Padrão                   | Descrição                      |
|-----------------------|--------------------------|--------------------------------|
| `MILVUS_HOST`         | `localhost`              | Host do Milvus                 |
| `MILVUS_PORT`         | `19530`                  | Porta do Milvus                |
| `MILVUS_COLLECTION`   | `cgmacros_embeddings`    | Collection no Milvus           |
| `OLLAMA_URL`          | `http://localhost:11434` | URL do Ollama                  |
| `EMBED_MODEL`         | `nomic-embed-text`       | Modelo de embedding            |
| `LLM_MODEL`           | `llama3.2`               | Modelo LLM padrão              |
| `LLM_MODEL_ALT`       | `mistral`                | Modelo LLM alternativo         |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000`  | URI do MLflow                  |
| `POSTGRES_HOST`       | `localhost`              | Host do PostgreSQL             |
| `POSTGRES_PORT`       | `5432`                   | Porta do PostgreSQL            |
| `POSTGRES_USER`       | `rag_user`               | Usuário do banco               |
| `POSTGRES_PASSWORD`   | `rag_pass`               | Senha do banco                 |
| `POSTGRES_DB`         | `rag_db`                 | Nome do banco de dados         |

---

## Exemplos de uso

### curl

```bash
# Pergunta com modelo padrão (llama3.2)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Como a glicose varia após o almoço?"}'

# Pergunta com segundo modelo (mistral)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Resumo do paciente CGMacros-039.", "model": "mistral"}'

# Metadados
curl http://localhost:8000/metadata

# Health
curl http://localhost:8000/health
```

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Usando llama3.2 (padrão)
r = requests.post(f"{BASE_URL}/ask", json={"question": "Qual o padrão glicêmico matinal?"})
print(r.json()["answer"])
print(r.json()["model_used"])  # "llama3.2"

# Usando mistral
r = requests.post(f"{BASE_URL}/ask", json={
    "question": "Resuma os dados do CGMacros-012.",
    "model": "mistral"
})
print(r.json()["model_used"])  # "mistral"
```

---

## Decisões Técnicas

**Nomenclatura `/ask` em vez de `/query`**  
O endpoint foi nomeado `/ask` pois o sistema responde perguntas em linguagem natural, não executa queries estruturadas.

**Seleção de modelo por chamada**  
O campo `model` no body permite escolher entre `llama3.2` e `mistral` sem reiniciar a API, facilitando comparações de qualidade de resposta.

**Persistência em PostgreSQL**  
Além do MLflow, os logs são salvos no PostgreSQL para facilitar consultas relacionais e análises históricas. Em caso de falha do banco, a API continua operando normalmente (fail-safe).

**`lru_cache` nas dependências**  
Os componentes pesados (Milvus, Ollama, MLflow) são inicializados uma única vez por instância, reduzindo latência e reconexões desnecessárias.