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

## Sprint 3 — Governança de Dados (Medallion Architecture)

Na Sprint 3 foi implementada a base da governança de dados utilizando a arquitetura Medallion, com organização em três camadas: Bronze, Silver e Gold.

### Evidências
- estruturação do bucket `cgmacros` no MinIO
- separação das camadas `bronze/`, `silver/` e `gold/`
- armazenamento dos dados brutos na camada Bronze
- preparação das camadas Silver e Gold para processamento e consumo analítico

### Estrutura do Data Lake

```bash
cgmacros/
├── bronze/
├── silver/
│   └── cgmacros_tratado.csv
└── gold/
    └── dataset_ml.csv
```
## Sprint 4 — Pipeline de Dados e Treinamento do Modelo

Na Sprint 4 foi desenvolvido o pipeline de dados integrando a arquitetura Medallion ao processo de Machine Learning.

### Evidências
- script `scripts/train_model.py`
- pasta `mlruns/`
- leitura dos dados diretamente da camada Bronze no MinIO
- geração de dados tratados na camada Silver
- geração de dataset final na camada Gold

### O que foi realizado
- leitura e consolidação dos arquivos CSV a partir do MinIO
- tratamento e limpeza dos dados
- criação de atributos temporais (hora, minuto, dia da semana e mês)
- engenharia de features
- geração da camada Silver com dados tratados
- preparação do dataset final para Machine Learning
- geração da camada Gold com dados prontos para treino
- separação entre treino e teste
- treinamento de modelo de regressão
- cálculo de métricas
- registro do experimento com MLflow

### Modelo utilizado
- RandomForestRegressor

### Métricas registradas
- MAE
- R²

### Resultado
Foi estruturado um pipeline de dados integrando as camadas Bronze, Silver e Gold ao treinamento do modelo, com rastreamento de parâmetros, métricas e artefatos no MLflow.

---

## Conclusão da AC1

Com base nas evidências presentes no repositório, o projeto já apresenta entregas compatíveis com as Sprints 1, 2, 3 e 4, contemplando:

- definição do produto  
- arquitetura inicial  
- infraestrutura base  
- governança de dados com arquitetura Medallion  
- pipeline de dados com geração de Bronze, Silver e Gold  
- modelagem com registro de experimentos no MLflow  

Essas etapas formam a base necessária para a evolução posterior do projeto em direção ao pipeline completo de embeddings, armazenamento vetorial e construção do fluxo RAG.