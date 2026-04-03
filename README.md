# Plataforma RAG com Governança de Dados

Projeto desenvolvido para a disciplina de Inteligência Artificial.

O objetivo é construir uma plataforma de **Retrieval-Augmented Generation (RAG)** para realizar consultas inteligentes sobre dados da área da saúde, com apoio de **governança de dados**, **infraestrutura local containerizada** e **experimentação com MLflow**.

---

## Visão Geral do Projeto

A proposta do projeto é desenvolver uma plataforma capaz de:

- organizar dados de saúde em uma arquitetura com governança;
- permitir consultas inteligentes sobre os dados;
- utilizar inteligência artificial para apoiar interpretação das informações;
- preparar a base para um fluxo de RAG;
- registrar experimentos e evolução de modelos com MLflow.

---

## Domínio

Saúde

## Dataset

CGMacros  
https://www.physionet.org/content/cgmacros/1.0.0/

## Empresa Fictícia

Laboratório de análises clínicas.

## Problema de Negócio

Atualmente, muitas informações relacionadas à saúde e nutrição estão distribuídas em diferentes bases de dados, o que dificulta a análise rápida e integrada dessas informações.

O problema que buscamos resolver é como permitir que usuários realizem consultas e compreendam melhor dados relacionados à saúde a partir de um conjunto de dados disponível, utilizando recursos de inteligência artificial e governança de dados.

## Levantamento de Requisitos

- Centralizar informações de saúde em um único sistema
- Permitir consultas inteligentes aos dados
- Utilizar inteligência artificial para auxiliar na interpretação das informações
- Facilitar o acesso e a compreensão dos dados disponíveis

---

# Organização por Sprint

## Sprint 1 — Definição do Produto

Nesta sprint foi realizada a definição inicial do projeto, incluindo o domínio, dataset, empresa fictícia, problema de negócio, requisitos e organização do time.

### Entregas da Sprint 1

- definição do domínio: **saúde**
- definição do dataset: **CGMacros**
- definição da empresa fictícia: **laboratório de análises clínicas**
- descrição do problema de negócio
- levantamento de requisitos funcionais iniciais
- definição de papéis Scrum
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

**Evidência da Sprint 1:** documentação inicial do produto e backlog descritos neste README.

---

## Sprint 2 — Arquitetura e Infraestrutura Base

Nesta sprint foi definida a arquitetura inicial da solução e estruturada a infraestrutura base para execução local do projeto.

### Componentes Arquiteturais

A arquitetura do projeto contempla os seguintes componentes principais:

- **Gradio / Interface de Chat** para interação com o usuário
- **API / Backend** para orquestração central
- **Ollama / LLM Local** para inferência
- **PostgreSQL** para metadados e auditoria
- **MinIO** como Data Lake
- **Milvus / Vector Store** previsto para armazenamento vetorial
- **MLflow** para rastreabilidade de experimentos
- **Pipeline de Embeddings e RAG** previstos na estrutura do projeto

### Infraestrutura Inicial

A infraestrutura local foi iniciada com Docker Compose, incluindo os seguintes serviços:

- **PostgreSQL**
- **MinIO**
- **Ollama**

### Evidências da Sprint 2

- `docker-compose.yml`
- `Makefile`
- pasta `docs/`
- estrutura modular em `src/`

### Arquitetura do Projeto


![Arquitetura do Projeto](docs/architecture/arquitetura.png)


---

## Sprint 3 — Governança de Dados e Ingestão

Nesta sprint foi iniciada a organização dos dados e da ingestão, com foco em estruturar a base do projeto em um fluxo de governança.

### Objetivo da Sprint 3

- realizar o download do dataset
- extrair arquivos compactados
- preparar os dados brutos
- enviar os dados para o Data Lake
- estruturar a base de ingestão para evolução da governança

### Fluxo Implementado

O projeto já possui automação para:

- baixar os dados da fonte original
- extrair arquivos `.zip`, `.tar.gz` e `.gz`
- configurar o MinIO local
- criar bucket de armazenamento
- enviar os dados para a camada Bronze no MinIO

### Evidências da Sprint 3

No `Makefile`, os comandos abaixo representam a base da ingestão:

- `download-data`
- `extract-data`
- `configure-minio`
- `upload-minio`
- `ingest-data`

Atualmente os dados brutos são enviados para:

- `cgmacros/bronze/`

### Relação com Governança

A Sprint 3 representa o início da organização governada dos dados, especialmente da camada **Bronze**, que concentra os dados brutos obtidos da fonte original. Essa base é importante para a evolução futura para etapas de tratamento, embeddings e consumo pela aplicação.

**Evidência da Sprint 3:** fluxo automatizado de ingestão e armazenamento inicial no MinIO.

---

## Sprint 4 — Modelagem e Experimentação com MLflow

Nesta sprint foi iniciada a etapa de modelagem com foco em construir uma base analítica para o projeto e registrar experimentos de forma rastreável.

### Objetivo da Sprint 4

- preparar os dados para treinamento
- definir uma variável alvo
- treinar um modelo de machine learning
- avaliar métricas de desempenho
- registrar parâmetros, métricas e artefatos com MLflow

### Problema Trabalhado

Foi utilizado o dataset CGMacros com foco em predição relacionada à coluna:

- **Dexcom GL**

### Etapas Realizadas no Treinamento

O script `scripts/train_model.py` realiza:

- leitura dos dados
- concatenação dos CSVs por paciente
- pré-processamento
- criação de atributos temporais
- geração de features cíclicas
- remoção de colunas não utilizadas
- separação entre treino e teste
- treinamento de modelo de regressão
- cálculo de métricas
- rastreamento com MLflow

### Modelo Utilizado

- **RandomForestRegressor**

### Métricas Registradas

- **MAE**
- **R²**

### Rastreamento com MLflow

O projeto registra no MLflow:

- parâmetros do experimento
- quantidade de linhas e features
- métricas do modelo
- artefato do modelo treinado

### Evidências da Sprint 4

- `scripts/train_model.py`
- pasta `mlruns/`

**Evidência da Sprint 4:** treinamento funcional com registro de experimento em MLflow.

---

# Estrutura do Repositório

```bash
IA/
├── docs/
├── mlruns/
├── scripts/
│   ├── cleanup_buckets.py
│   └── train_model.py
├── src/
│   ├── api/
│   ├── config/
│   ├── data/
│   ├── database/
│   ├── docker/
│   ├── embeddings/
│   ├── ingestion/
│   ├── llm/
│   ├── mlops/
│   ├── rag/
│   ├── scripts/
│   ├── ui/
│   └── vector_store/
├── .env
├── .gitignore
├── docker-compose.yml
├── example.env
├── Makefile
├── README.md
└── requirements.txt
```

---

# Tecnologias Utilizadas

- Python
- Docker
- Docker Compose
- PostgreSQL
- MinIO
- Ollama
- MLflow
- Uvicorn / FastAPI
- Scikit-learn
- Pandas
- NumPy

---

# Como Executar

## 1. Subir infraestrutura

```bash
make up
```

## 2. Executar a aplicação local

```bash
make app
```

## 3. Executar ingestão de dados

```bash
make ingest-data
```

Esse fluxo realiza:

- download do dataset
- extração dos arquivos
- configuração do MinIO
- upload dos dados para a camada Bronze

## 4. Executar treinamento do modelo

```bash
python scripts/train_model.py
```

---

# Serviços da Infraestrutura

## PostgreSQL
Responsável por metadados e suporte à arquitetura da aplicação.

## MinIO
Responsável pelo armazenamento dos dados no Data Lake.

## Ollama
Responsável pela camada de modelo local utilizada na arquitetura do projeto.

---

# Evidências da AC1

A AC1 contempla principalmente as entregas até a Sprint 4.  
No estado atual do projeto, as seguintes evidências podem ser identificadas:

- **Sprint 1:** definição do produto, domínio, empresa fictícia, problema, requisitos, backlog e papéis Scrum
- **Sprint 2:** arquitetura definida e infraestrutura inicial com Docker Compose
- **Sprint 3:** ingestão automatizada de dados e armazenamento da camada Bronze no MinIO
- **Sprint 4:** treinamento de modelo com métricas e rastreamento de experimento em MLflow

---

# Próximos Passos

As próximas etapas do projeto envolvem a evolução da plataforma para:

- pipeline de embeddings
- armazenamento vetorial
- construção do fluxo RAG
- integração completa entre backend, LLM e recuperação de contexto
- interface de consulta ao usuário

---

# Equipe

Projeto desenvolvido por alunos da disciplina de Inteligência Artificial.

Gabriel Habila Pinheiro – RA: 211981  
Isabelle Munhoz Scarso – RA: 223285  
Gabriela Zala Coutinho Arruda – RA: 212191  
Cainã Jose Arruda Pinto – RA: 210626  
Leonardo Braz de Almeida Fonseca – RA: 212092  
André Lucas Costa Pereira – RA: 200431  
Lara Beatriz Costa Sabino – RA: 223228  
Bruno de Oliveira Malena – RA: 222449  
Rafael Ferro Machado – RA: 223347  
Henry Santuriao Almeida – RA: 211726