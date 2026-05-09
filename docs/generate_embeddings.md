# Documentação do Script generate_embeddings.py

## Visão Geral
O script `generate_embeddings.py` é responsável por gerar embeddings de texto a partir de dados de pacientes armazenados em arquivos Parquet no MinIO, utilizando o Ollama para embeddings e indexando os vetores no Milvus. Ele processa múltiplos pacientes em paralelo usando ThreadPoolExecutor.

## Funcionalidades Principais
- Leitura de dados de pacientes do MinIO.
- Conversão de linhas de DataFrame em textos representativos.
- Geração de embeddings via Ollama.
- Indexação dos embeddings no Milvus.

## Dependências e Classes Utilizadas

### PatientIdentifier
Classe que representa um identificador de paciente e gera a chave do arquivo Parquet no MinIO.

- **Método `to_gold_parquet_key()`**: Retorna a chave do arquivo, ex.: `gold/CGMacros/CGMacros-012/CGMacros-012_ML_READY.parquet`.

### GoldPatientDataFrame
Classe que encapsula um DataFrame Pandas lido de bytes Parquet.

- **Método `training_rows()`**: Retorna 80% das linhas ordenadas por Timestamp para treinamento.
- **Método `row_count()`**: Retorna o número total de linhas.

### GoldParquetReader
Classe para ler arquivos Parquet do MinIO.

- **Método `read(patient_identifier)`**: Baixa o arquivo, lê os bytes e retorna um `GoldPatientDataFrame`.

### RowTextRepresentation
Classe que converte uma linha do DataFrame em uma string de texto.

- **Método `build()`**: Junta colunas e valores com " | ", ex.: `col1: val1 | col2: val2`.

### DataFrameTextCollection
Classe que converte um DataFrame inteiro em uma lista de textos.

- **Método `as_texts()`**: Retorna lista de strings, uma por linha.

### EmbeddingVector
Classe que representa um vetor de embedding.

- **Método `as_list()`**: Retorna a lista de floats.
- **Método `dimension()`**: Retorna a dimensão do vetor.

### OllamaEmbedder
Classe para gerar embeddings usando a API do Ollama.

- **Método `embed(text)`**: Envia o texto para `/api/embeddings` e retorna um `EmbeddingVector`.

### MilvusCollectionFactory
Classe para gerenciar conexão e criação de coleção no Milvus.

- **Método `connect()`**: Conecta ao Milvus.
- **Método `get_or_create(dimension)`**: Obtém ou cria coleção com campos id (INT64), text (VARCHAR), embedding (FLOAT_VECTOR).

### MilvusRecordBatch
Classe para batch de registros a inserir no Milvus.

- **Método `add(record_id, text, embedding)`**: Adiciona um registro ao batch.
- **Método `flush_into(collection)`**: Insere o batch na coleção e retorna o número de registros inseridos.

## Fluxo de Execução
1. Configura cliente MinIO e fábrica de coleção Milvus.
2. Para cada paciente, submete tarefa ao ThreadPoolExecutor.
3. Em cada tarefa:
   - Lê dados do paciente via GoldParquetReader.
   - Converte linhas em textos via DataFrameTextCollection.
   - Gera embeddings para cada texto via OllamaEmbedder.
   - Adiciona ao batch MilvusRecordBatch.
   - Insere batch na coleção Milvus.
4. Aguarda conclusão de todas as tarefas.

## Variáveis de Ambiente
- `MINIO_ENDPOINT`: Endpoint MinIO (padrão: localhost:9000)
- `MINIO_BUCKET`: Bucket MinIO (padrão: cgmacros)
- `OLLAMA_URL`: URL Ollama (padrão: http://localhost:11434)
- `EMBED_MODEL`: Modelo de embedding (padrão: nomic-embed-text)
- `MILVUS_HOST`: Host Milvus (padrão: localhost)
- `MILVUS_PORT`: Porta Milvus (padrão: 19530)
- `MILVUS_COLLECTION`: Nome da coleção (padrão: cgmacros_embeddings)
- `EMBED_WORKERS`: Número de workers (padrão: 4)
- `MINIO_USER`: Usuário MinIO
- `MINIO_PASSWORD`: Senha MinIO

## Execução
Execute o script diretamente:
```
python src/scripts/generate_embeddings.py
```

## Saída
Imprime o número de vetores indexados por paciente, ex.: `[embeddings] CGMacros-012 → 500 vetores indexados`.
