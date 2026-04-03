# AC1 — Evidências das Sprints 1 a 4

Este documento resume as evidências desenvolvidas no projeto até a **Sprint 4**, conforme a proposta da disciplina de Inteligência Artificial.

---

## Sprint 1 — Definição do Produto

Na Sprint 1 foi realizada a definição inicial do projeto, incluindo o contexto de negócio, o domínio, o dataset, os requisitos e a organização do time.

### Evidências
- definição do domínio: **saúde**
- definição do dataset: **CGMacros**
- definição da empresa fictícia: **laboratório de análises clínicas**
- definição do problema de negócio
- levantamento de requisitos iniciais
- definição dos papéis Scrum
- criação do backlog inicial

### Resultado
Foi estabelecida a base conceitual do projeto, deixando claro o que será construído, para quem e com qual objetivo.

---

## Sprint 2 — Arquitetura e Infraestrutura Base

Na Sprint 2 foi definida a arquitetura inicial da solução e estruturada a infraestrutura local para suportar a evolução do projeto.

### Evidências
- diagrama arquitetural do sistema
- arquivo `docker-compose.yml`
- arquivo `Makefile`
- estrutura modular do projeto em `src/`

### Serviços já considerados na arquitetura
- interface de usuário
- backend / orquestração
- PostgreSQL
- MinIO
- Ollama
- MLflow
- estrutura prevista para embeddings, vector store e RAG

### Resultado
Foi criada a base arquitetural e de infraestrutura necessária para suportar as próximas etapas do projeto.

---

## Sprint 3 — Governança de Dados e Ingestão

Na Sprint 3 foi iniciada a organização da ingestão e do armazenamento dos dados, com foco na camada inicial de governança.

### Evidências
No `Makefile`, já existe automação para:

- `download-data`
- `extract-data`
- `configure-minio`
- `upload-minio`
- `ingest-data`

### Fluxo implementado
- download do dataset a partir da fonte original
- extração de arquivos compactados
- configuração do MinIO local
- criação do bucket
- upload dos dados brutos para a camada Bronze

### Resultado
Foi implementada a base da ingestão governada dos dados, com armazenamento inicial da camada **Bronze** no MinIO.

---

## Sprint 4 — Modelagem e Experimentação com MLflow

Na Sprint 4 foi iniciada a etapa de modelagem e rastreabilidade dos experimentos.

### Evidências
- script `scripts/train_model.py`
- pasta `mlruns/`

### O que foi realizado
- leitura e concatenação dos arquivos do dataset
- pré-processamento dos dados
- criação de atributos temporais
- preparação das features numéricas
- separação entre treino e teste
- treinamento de modelo de regressão
- cálculo de métricas
- registro do experimento com MLflow

### Modelo utilizado
- `RandomForestRegressor`

### Métricas registradas
- `MAE`
- `R²`

### Resultado
Foi implementado um fluxo inicial de treinamento com rastreamento de parâmetros, métricas e modelo no MLflow, consolidando a base da Sprint 4.

---

## Conclusão da AC1

Com base nas evidências presentes no repositório, o projeto já apresenta entregas compatíveis com as Sprints 1, 2, 3 e 4, contemplando:

- definição do produto
- arquitetura inicial
- infraestrutura base
- ingestão e armazenamento inicial de dados
- modelagem com registro de experimentos

Essas etapas formam a base necessária para a evolução posterior do projeto em direção ao pipeline completo de embeddings, armazenamento vetorial e construção do fluxo RAG.