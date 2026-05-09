# Localização dos Componentes do RAG

## Busca Vetorial
A busca vetorial é realizada pela classe `MilvusSemanticSearcher` localizada em `src/embeddings/semantic_searcher.py`. Esta classe utiliza o Milvus para buscar os vetores mais similares com base em embeddings.

- **Método principal**: `search(embedding, top_k)` - Executa busca ANN no campo "embedding" da coleção Milvus.
- **Resultado**: Retorna `SearchResultCollection` com textos dos hits.

A busca é integrada no `ContextRetriever` em `src/rag/retriever.py`, que combina o embedder (`OllamaEmbedder`) para gerar o embedding da query e o searcher para recuperar contexto.

## Construção de Prompt
A construção de prompt é feita pela classe `PromptBuilder` em `src/rag/prompt_builder.py`. Utiliza um template fixo que inclui contexto recuperado, predição de glicose e a pergunta do usuário.

- **Template**: Inclui instruções para o assistente, dados relevantes, predição e pergunta.
- **Método**: `build(question, context, prediction)` - Retorna `RagPrompt` com o prompt completo.

## Integração com LLM
A integração com o LLM é gerenciada pela classe `OllamaLlmClient` em `src/rag/rag_pipeline.py`. Faz chamadas para a API do Ollama para gerar respostas baseadas no prompt.

- **Método**: `generate(prompt)` - Envia POST para `/api/generate` e retorna `LlmResponse` com o texto gerado.
- **Configuração**: Usa URL base e nome do modelo (ex.: llama3.2).

## RAG Funcionando via Script
O pipeline RAG completo é implementado na classe `RagPipeline` em `src/rag/rag_pipeline.py`. Ele orquestra a recuperação de contexto, predição de glicose e geração de resposta.

- **Fluxo**:
  1. `ContextualPredictor.resolve(question)`: Recupera contexto via `ContextRetriever` e faz predição com `RidgeGlucosePredictor`.
  2. `PromptBuilder.build()`: Constrói o prompt.
  3. `OllamaLlmClient.generate()`: Gera resposta.

O RAG é executado via API em `src/api/main.py` (endpoint POST /ask), mas também pode ser testado diretamente via scripts como `src/scripts/search_embeddings.py` para busca vetorial isolada.

Para executar o pipeline completo via script, pode-se criar um script que instancie `RagPipeline` e chame `answer(question)`.
