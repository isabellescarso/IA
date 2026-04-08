olha esse codigo aqui 
# Plataforma RAG com Governança de Dados

Projeto desenvolvido para a disciplina de Inteligência Artificial.

O objetivo do projeto é construir uma plataforma local de **Retrieval-Augmented Generation (RAG)** para consultas inteligentes sobre dados da área da saúde, utilizando **governança de dados**, **arquitetura Medallion**, **armazenamento em Data Lake com MinIO**, **busca vetorial com Milvus**, **inferência com LLM local via Ollama**, **API com FastAPI**, **interface com Gradio** e **rastreamento de experimentos com MLflow**.

---

## Visão Geral do Projeto

A proposta do projeto foi desenvolver uma plataforma capaz de:

- organizar dados de saúde em um ambiente governado;
- estruturar os dados em camadas Bronze, Silver e Gold;
- preparar dados para Machine Learning e para recuperação semântica;
- gerar embeddings e indexar vetores em banco vetorial;
- responder perguntas em linguagem natural por meio de um fluxo RAG;
- disponibilizar uma API e uma interface de consulta;
- registrar experimentos e avaliações com MLflow;
- automatizar a execução com Docker Compose e Makefile.

---

## Domínio

Saúde

---

## Dataset

CGMacros  
https://www.physionet.org/content/cgmacros/1.0.0/

---

## Empresa Fictícia

Laboratório de análises clínicas.

---

## Problema de Negócio

Atualmente, informações relacionadas à saúde e à nutrição podem estar distribuídas em diferentes arquivos e formatos, dificultando sua análise integrada e a extração de conhecimento útil.

O problema que este projeto busca resolver é como permitir que usuários consultem dados clínicos e nutricionais em linguagem natural, obtendo respostas contextualizadas a partir de um pipeline de recuperação semântica e geração com inteligência artificial, apoiado por governança de dados e infraestrutura local.

---

## Objetivos do Projeto

- Centralizar dados de saúde em uma estrutura organizada
- Aplicar governança de dados com arquitetura Medallion
- Preparar datasets para análise, treino e consulta
- Implementar pipeline de embeddings e indexação vetorial
- Construir um fluxo RAG funcional ponta a ponta
- Disponibilizar API para consulta
- Disponibilizar interface simples para interação com o usuário
- Registrar métricas, parâmetros e execuções no MLflow

---

# Organização por Sprint

## Sprint 1 — Definição do Produto

Nesta sprint foi realizada a definição inicial do projeto, incluindo domínio, dataset, empresa fictícia, problema de negócio, requisitos e organização do time.

### Entregas da Sprint 1

- definição do domínio: **saúde**
- definição do dataset: **CGMacros**
- definição da empresa fictícia: **laboratório de análises clínicas**
- descrição do problema de negócio
- levantamento de requisitos funcionais iniciais
- definição dos papéis Scrum
- criação do Product Backlog inicial

### Product Backlog Inicial

- Permitir consultas sobre dados de saúde utilizando linguagem natural
- Organizar e disponibilizar dados para consulta
- Permitir interpretação dos dados através de inteligência artificial
- Exibir respostas de forma clara para o usuário

### Papéis Scrum

**Product Owner**  
Isabelle Munhoz Scarso – RA: 223285

**Scrum Master**  
Rafael Ferro Machado – RA: 223347

**Time de Desenvolvimento**  
Gabriel Habila Pinheiro – RA: 211981  
Gabriela Zala Coutinho Arruda – RA: 212191  
Cainã Jose Arruda Pinto – RA: 210626  
Leonardo Braz de Almeida Fonseca – RA: 212092  
André Lucas Costa Pereira – RA: 200431  
Lara Beatriz Costa Sabino – RA: 223228  
Bruno de Oliveira Malena – RA: 222449  
Henry Santuriao Almeida – RA: 211726

**Evidência da Sprint 1:** definição do produto, equipe, backlog e contexto de negócio documentados no repositório.

---

## Sprint 2 — Arquitetura e Infraestrutura Base

Nesta sprint foi definida a arquitetura geral da solução e foi estruturada a infraestrutura inicial para execução local do projeto.



### Componentes Arquiteturais

A arquitetura atual do projeto contempla os seguintes componentes:

- **FastAPI** para disponibilização da API
- **Gradio** para interface de consulta
- **MinIO** como Data Lake local
- **Milvus** como banco vetorial
- **Ollama** para geração de embeddings e inferência com LLM local
- **MLflow** para rastreamento de experimentos
- **Makefile** para automação de comandos
- **Docker Compose** para orquestração dos serviços

### Infraestrutura Inicial

A infraestrutura local foi organizada com Docker Compose, incluindo serviços para:

- **MinIO**
- **Ollama**
- **etcd**
- **Milvus**

### Evidências da Sprint 2

- `docker-compose.yml`
- `Makefile`
- pasta `docs/architecture/`
- estrutura modular em `src/`

### Arquitetura do Projeto

A documentação arquitetural foi organizada na pasta `docs/architecture/`, incluindo descrição do fluxo geral do RAG e diagrama da solução.

![Arquitetura do Projeto](docs/architecture/arquitetura.png)

---

## Sprint 3 — Governança de Dados (Medallion Architecture)

Nesta sprint foi implementada a base da governança de dados com organização em camadas Bronze, Silver e Gold.

### Estrutura de Dados

A governança foi estruturada com separação lógica entre:

- **Bronze:** dados brutos ingeridos no sistema
- **Silver:** dados tratados e estruturados
- **Gold:** dados prontos para consumo analítico, treino e embeddings

### Atividades realizadas

- preparação da estrutura de dados para a arquitetura Medallion
- criação de pipeline de ingestão
- organização dos dados por camadas
- preparação do ambiente para transformação e reutilização dos dados
- definição de fluxo para consumo dos dados pela etapa de ML e pela etapa de embeddings

### Evidência da Sprint 3

- módulos de ingestão em `src/ingestion/`
- scripts de ingestão em `src/scripts/ingest/`
- estrutura de dados em `src/data/`
- documentação arquitetural da governança

---

## Sprint 4 — Pipeline de Dados e Treinamento do Modelo

Nesta sprint foi desenvolvido o pipeline de treinamento com leitura da camada Gold e rastreamento via MLflow.

### Fluxo do Pipeline

```text
Bronze → Silver → Gold → Treinamento
```

### Etapas realizadas

- leitura dos dados da camada Gold no MinIO
- carregamento de dados por paciente
- junção dos dados em um único dataset
- separação temporal entre treino e teste
- definição da variável alvo
- treinamento de modelo de regressão com Random Forest
- cálculo de métricas de avaliação
- registro de parâmetros, métricas, modelo e importância de features no MLflow

### Tecnologias utilizadas

- Python
- pandas
- scikit-learn
- MinIO
- MLflow

### Resultado

Foi estruturado um pipeline de treinamento funcional integrado à camada Gold, permitindo rastreabilidade dos experimentos e base organizada para evolução analítica do projeto.

### Evidência da Sprint 4

- `src/scripts/train_model.py`
- `src/mlops/training_tracker.py`
- `mlruns/`

---

## Sprint 5 — Pipeline de Embeddings

Nesta sprint foi implementada a etapa de geração de embeddings a partir dos dados preparados.

### Etapas realizadas

- leitura dos dados Gold no MinIO
- conversão dos registros em representações textuais
- geração de embeddings com modelo local via Ollama
- criação e uso de coleção no Milvus
- indexação dos vetores gerados

### Resultado

Foi estabelecido um pipeline de embeddings funcional, permitindo a indexação vetorial dos dados preparados e viabilizando a recuperação semântica.

### Evidência da Sprint 5

- `src/scripts/generate_embeddings.py`
- módulos em `src/embeddings/`
- integração com Milvus e Ollama

---

## Sprint 6 — Construção do RAG Core

Nesta sprint foi consolidado o núcleo do pipeline RAG.

### Componentes implementados

- Retriever para recuperação de contexto
- PromptBuilder para montagem do prompt
- RagPipeline para orquestração da pergunta, recuperação e geração
- integração entre embeddings, recuperação vetorial e LLM

### Fluxo do RAG

```text
Pergunta do usuário
→ Geração do embedding da consulta
→ Busca vetorial no Milvus
→ Recuperação do contexto
→ Construção do prompt
→ Geração de resposta com Ollama
→ Retorno ao usuário
```

### Evidência da Sprint 6

- `src/rag/retriever.py`
- `src/rag/prompt_builder.py`
- `src/rag/rag_pipeline.py`

---

## Sprint 7 — API

Nesta sprint foi estruturada a API da aplicação com FastAPI.

### Endpoints principais

- `GET /health` — verificação de disponibilidade
- `POST /ask` — consulta ao pipeline RAG
- `GET /metadata` — retorno de metadados do sistema

### Resultado

A aplicação passou a disponibilizar um contrato de API para integração com interface e validação do pipeline.

### Evidência da Sprint 7

- `src/api/main.py`
- `src/api/dependencies.py`
- `src/api/routes/ask.py`
- `src/api/routes/metadata.py`
- `src/api/routes/health.py`

---

## Sprint 8 — Interface

Nesta sprint foi implementada uma interface simples em Gradio para interação com o sistema.

### Funcionalidades

- campo de pergunta em linguagem natural
- envio da pergunta para a API
- exibição da resposta retornada pelo pipeline RAG

### Evidência da Sprint 8

- `src/ui/gradio_app.py`

---

## Sprint 9 — Avaliação e MLflow

Nesta sprint foi adicionada a avaliação de variantes de prompt e o registro de execuções.

### Atividades realizadas

- definição de variantes de prompt
- execução comparativa das variantes
- registro de resultados no MLflow
- medição de tempo de resposta e tamanho das saídas
- rastreamento das consultas realizadas ao sistema

### Evidência da Sprint 9

- `src/scripts/evaluate_prompts.py`
- `src/mlops/prompt_evaluator.py`
- `src/mlops/ask_tracker.py`

---

## Sprint 10 — Automação e Validação

Nesta sprint foi fortalecida a automação do ambiente e a validação do sistema.

### Comandos automatizados

- subir e derrubar infraestrutura
- executar API
- executar interface
- abrir MLflow
- rodar pipeline de ingestão
- rodar treino
- gerar embeddings
- avaliar prompts
- validar funcionamento do sistema

### Validação final

Foi implementado um script de validação com verificações de:

- API health
- metadata
- coleção no Milvus
- resposta do pipeline RAG

### Evidência da Sprint 10

- `Makefile`
- `src/scripts/validate_system.py`

---

## Estrutura do Repositório

```text
IA/
├── docs/
│   └── architecture/
├── mlruns/
├── src/
│   ├── api/
│   │   └── routes/
│   ├── data/
│   ├── embeddings/
│   ├── ingestion/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   ├── mlops/
│   ├── rag/
│   ├── scripts/
│   │   ├── eda/
│   │   └── ingest/
│   └── ui/
├── .gitignore
├── docker-compose.yml
├── Makefile
├── README.md
├── requirements.txt
└── exemple.env
```

---

## Tecnologias Utilizadas

- Python
- FastAPI
- Gradio
- Docker
- Docker Compose
- MinIO
- Milvus
- Ollama
- MLflow
- scikit-learn
- pandas
- NumPy

---

## Como Executar

### 1. Subir a infraestrutura

```bash
make up
```

### 2. Rodar a API

```bash
make api
```

### 3. Rodar a interface

```bash
make ui
```

### 4. Rodar o MLflow

```bash
make mlflow
```

### 5. Executar o pipeline de treinamento

```bash
make train
```

### 6. Gerar embeddings

```bash
make embeddings
```

### 7. Avaliar prompts

```bash
make evaluate-prompts
```

### 8. Validar o sistema

```bash
make validate
```

---

## Serviços da Infraestrutura

**MinIO**  
Responsável pelo armazenamento do Data Lake e pela organização dos dados em camadas de governança.

**Ollama**  
Responsável pela inferência local do modelo de linguagem e pela geração de embeddings.

**etcd**  
Responsável por suportar a execução do Milvus.

**Milvus**  
Responsável pelo armazenamento vetorial e pela recuperação semântica dos dados indexados.

**MLflow**  
Responsável pelo rastreamento de experimentos de treino, avaliação de prompts e execuções da aplicação.

---

## Entregáveis Atendidos no Estado Atual do Projeto

Com base no estado atual do repositório, é possível identificar os seguintes entregáveis já contemplados:

- Docker Compose funcional
- Makefile com comandos padronizados
- documentação arquitetural
- pipeline de embeddings
- recuperação vetorial com Milvus
- RAG funcionando via API
- interface de consulta com Gradio
- rastreamento de experimentos com MLflow
- backlog e organização por sprint documentados

---

## Justificativa das Decisões Técnicas

- **MinIO** foi utilizado para representar um Data Lake local com suporte à arquitetura Medallion.
- **Milvus** foi escolhido para armazenamento vetorial e busca semântica.
- **Ollama** permitiu uso local de modelos para geração e embeddings.
- **FastAPI** foi adotado pela simplicidade de criação de endpoints e documentação automática.
- **Gradio** foi utilizado para disponibilizar uma interface simples de demonstração.
- **MLflow** foi escolhido para rastrear métricas, parâmetros, variantes de prompt e execuções.
- **Docker Compose** foi utilizado para padronizar a infraestrutura do grupo.
- **Makefile** foi utilizado para centralizar os comandos operacionais do projeto.

---

## Próximos Passos

As próximas evoluções possíveis do projeto incluem:

- ampliação do número de pacientes e documentos utilizados
- melhoria da estratégia de chunking e recuperação
- expansão dos testes de avaliação do RAG
- refinamento dos prompts
- ampliação da documentação técnica
- evolução da interface para um frontend mais robusto

---

## Equipe

Projeto desenvolvido por alunos da disciplina de Inteligência Artificial.

| Nome | RA |
|------|----|
| Gabriel Habila Pinheiro | 211981 |
| Isabelle Munhoz Scarso | 223285 |
| Gabriela Zala Coutinho Arruda | 212191 |
| Cainã Jose Arruda Pinto | 210626 |
| Leonardo Braz de Almeida Fonseca | 212092 |
| André Lucas Costa Pereira | 200431 |
| Lara Beatriz Costa Sabino | 223228 |
| Bruno de Oliveira Malena | 222449 |
| Rafael Ferro Machado | 223347 |
| Henry Santuriao Almeida | 211726 |