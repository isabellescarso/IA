# Documentação da API

## Visão Geral
A API RAG CGMacros é construída com FastAPI e fornece endpoints para verificações de saúde, perguntas via pipeline RAG e recuperação de metadados. Integra-se com Milvus para busca vetorial, Ollama para embeddings e LLM, e MLflow para rastreamento de modelos.

## Variáveis de Ambiente
- `MILVUS_HOST`: Host do Milvus (padrão: localhost)
- `MILVUS_PORT`: Porta do Milvus (padrão: 19530)
- `MILVUS_COLLECTION`: Nome da coleção Milvus (padrão: cgmacros_embeddings)
- `OLLAMA_URL`: URL do servidor Ollama (padrão: http://localhost:11434)
- `EMBED_MODEL`: Modelo de embedding (padrão: nomic-embed-text)
- `LLM_MODEL`: Modelo LLM (padrão: llama3.2)
- `MLFLOW_TRACKING_URI`: URI de rastreamento MLflow (padrão: http://localhost:5000)

## Endpoints

### GET /health
Endpoint de verificação de saúde.

**Resposta:**
```json
{
  "status": "ok"
}
```

### POST /ask
Faça uma pergunta ao sistema RAG. O sistema recupera contexto relevante usando embeddings, prevê níveis de glicose e gera uma resposta usando o LLM.

**Corpo da Requisição:**
```json
{
  "question": "string"
}
```

**Resposta:**
```json
{
  "answer": "string"
}
```

### GET /metadata
Recupere metadados do sistema, incluindo total de vetores, pacientes e nomes de modelos.

**Resposta:**
```json
{
  "total_vectors": "integer",
  "patients": ["CGMacros-012", "CGMacros-039"],
  "embed_model": "string",
  "llm_model": "string"
}
```

## Executando a API
Para executar a API, use o seguinte comando:
```
uvicorn src.api.main:app --reload
```

A documentação interativa da API está disponível em `/docs` durante a execução.
