# Resumo dos Sprints 5 a 8

## Sprint 5 - Pipeline de Embeddings

**Objetivo:** Criar o pipeline para geração de embeddings a partir dos dados preparados

**Atividades realizadas:**
- Leitura dos dados Gold no MinIO
- Conversão dos registros em representações textuais
- Geração de embeddings com modelo local via Ollama
- Criação e uso de coleção no Milvus
- Indexação dos vetores gerados

**Como foi feito:**
Implementei o pipeline de embeddings em `src/scripts/generate_embeddings.py` que:
- Conecta ao MinIO para ler dados em formato Parquet
- Converte registros em textos representativos usando `DataFrameTextCollection`
- Gera embeddings usando `OllamaEmbedder` com modelo `nomic-embed-text`
- Indexa os vetores no Milvus através de `MilvusRecordBatch`
- Processa múltiplos pacientes em paralelo usando ThreadPoolExecutor

**Entregável:**
Pipeline de embeddings funcional com integração completa ao Milvus

## Sprint 6 - Construção do RAG Core

**Objetivo:** Consolidar o núcleo completo do pipeline RAG (Retrieval-Augmented Generation)

**Atividades realizadas:**
- Implementação da busca vetorial com integração ao Milvus
- Construção de prompts personalizados para o sistema
- Integração com LLM local via Ollama
- Criação de pipelines completos de recuperação e geração

**Como foi feito:**
Implementei três classes principais no diretório `src/rag/`:
- `ContextRetriever`: Responsável por buscar contextos relevantes usando embeddings e Milvus
- `PromptBuilder`: Monta o prompt com base no contexto recuperado
- `RagPipeline`: Coordena todo o fluxo do RAG com recuperação, construção do prompt e geração de resposta

**Entregável:**
RAG funcionando via script com todas as etapas integradas

## Sprint 7 - API (AC2)

**Objetivo:** Criar API REST para expor o funcionamento do RAG

**Atividades realizadas:**
- Construção de FastAPI com endpoints específicos
- Criação de validadores de entrada/saída
- Integração com a funcionalidade do RAG
- Implementação de tracking de experimentos

**Como foi feito:**
Implementei a estrutura completa da API no diretório `src/api/` com:
- Endpoints `/ask` para consultas ao RAG
- Endpoint `/metadata` para informações do sistema
- Integração com `AskExperimentTracker` para rastrear execuções
- Configuração de dependências via `src/api/dependencies.py`
- Validação de inputs e outputs com Pydantic

**Entregável:**
API documentada com endpoints bem definidos e funcional

## Sprint 8 - Interface

**Objetivo:** Criar uma interface simples e intuitiva para interagir com o sistema

**Atividades realizadas:**
- Implementação de interface Gradio
- Criação de campos para consulta e seleção de modelo
- Integração com a API para exibição de respostas

**Como foi feito:**
Criei a interface web em `src/ui/gradio_app.py` com:
- Campo de texto para perguntas
- Dropdown para seleção de modelos (llama3.2 ou mistral)
- Área de exibição de respostas
- Cliente HTTP para comunicação com a API
- Configuração para rodar no port 7860

**Entregável:**
Interface funcional com acesso direto ao RAG por meio de uma UI intuitiva

## Arquitetura Completa Implementada

O projeto segue uma arquitetura em camadas:

1. **Ingestão e Governança**: Dados tratados em Bronze, Silver e Gold
2. **Processamento**: Pipeline de embeddings com Milvus e Ollama
3. **RAG Core**: Componentes de recuperação e geração
4. **API**: FastAPI para exposição de recursos
5. **Interface**: Gradio para interação direta do usuário

## Fluxo de Funcionamento Completo

1. Dados são ingeridos e armazenados em camadas Gold
2. Pipeline de embeddings gera vetores e os indexa no Milvus
3. Usuário faz pergunta através da interface Gradio
4. A pergunta é enviada para a API FastAPI
5. API chama o pipeline RAG completo:
   - Recupera contexto relevante do Milvus
   - Faz previsão com base nos dados recuperados
   - Monta prompt com informações relevantes
   - Gera resposta com LLM local via Ollama
6. Resposta é retornada ao usuário através da interface

## Tecnologias Utilizadas

- **Python** com bibliotecas especializadas
- **FastAPI** para a API REST
- **Gradio** para interface web
- **Ollama** para inferência local
- **Milvus** para busca vetorial
- **Docker Compose** para orquestração
- **MLflow** para rastreamento de experimentos

## Diretórios e Arquivos Principais

- `src/rag/`: Componentes do pipeline RAG
- `src/api/`: Servidor API FastAPI
- `src/ui/`: Aplicação Gradio de interface
- `src/embeddings/`: Módulos de geração e busca de embeddings
- `src/scripts/generate_embeddings.py`: Pipeline de geração de embeddings
- `docker-compose.yml`: Configuração de toda a infraestrutura
- `Makefile`: Comandos automatizados de execução

Cada sprint foi desenvolvido de forma incremental, mantendo consistência com a arquitetura geral do projeto, permitindo uma implementação completa desde a base de dados até a interface final com o usuário.