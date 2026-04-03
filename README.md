# Plataforma RAG com Governança de Dados

Projeto desenvolvido para a disciplina de Inteligência Artificial.

O objetivo é construir uma plataforma de **Retrieval-Augmented Generation (RAG)** para realizar consultas inteligentes sobre dados da área da saúde, com apoio de **governança de dados**, **infraestrutura local containerizada**, **arquitetura Medallion** e **rastreamento de experimentos com MLflow**.

---

## Visão Geral do Projeto

A proposta do projeto é desenvolver uma plataforma capaz de:

- organizar dados de saúde em um Data Lake com governança;
- permitir consultas inteligentes sobre esses dados;
- utilizar inteligência artificial para apoiar a interpretação das informações;
- preparar a base para evolução de um fluxo de RAG;
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

**Evidência da Sprint 1:** definição do produto, contexto de negócio, equipe e backlog inicial documentados neste README.

---

## Sprint 2 — Arquitetura e Infraestrutura Base

Nesta sprint foi definida a arquitetura inicial da solução e estruturada a infraestrutura base para execução local do projeto.

### Componentes Arquiteturais

A arquitetura do projeto contempla os seguintes componentes principais:

- **Interface / Frontend** para interação com o usuário
- **API / Backend** para orquestração central
- **Ollama / LLM Local** para inferência
- **PostgreSQL** para metadados e auditoria
- **MinIO** como Data Lake
- **Milvus / Vector Store** previsto para armazenamento vetorial
- **MLflow** para rastreabilidade de experimentos
- **Pipeline de embeddings e RAG** previstos na evolução da plataforma

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

## Sprint 3 — Governança de Dados (Medallion Architecture)

Nesta sprint foi implementada a base da governança de dados utilizando a arquitetura Medallion, com organização em três camadas: Bronze, Silver e Gold.

### Estrutura do Data Lake (MinIO)

O bucket principal `cgmacros` foi estruturado da seguinte forma:

```bash
cgmacros/
├── bronze/
├── silver/
└── gold/
```

### Camadas

- **Bronze:** armazenamento dos dados brutos, sem qualquer tratamento
- **Silver:** camada destinada ao tratamento, limpeza e enriquecimento dos dados
- **Gold:** camada final, com dados preparados para análise e treinamento de modelos

### Atividades realizadas

- Download do dataset CGMacros
- Organização dos arquivos por paciente
- Upload dos dados para o MinIO na camada Bronze
- Estruturação do Data Lake com separação em Bronze, Silver e Gold
- Preparação do ambiente para processamento e transformação dos dados

### Estrutura atual do Data Lake

```bash
cgmacros/
├── bronze/
├── silver/
│   └── cgmacros_tratado.csv
└── gold/
    └── dataset_ml.csv
```

Essa estrutura permite a separação clara entre dados brutos, dados tratados e dados prontos para consumo analítico, seguindo boas práticas de engenharia de dados.

**Evidência da Sprint 3:** estruturação do Data Lake no MinIO com separação das camadas Bronze, Silver e Gold, permitindo a organização governada do pipeline de dados.

---

## Sprint 4 — Pipeline de Dados e Treinamento do Modelo

Nesta sprint foi desenvolvido o pipeline de dados integrando a arquitetura Medallion ao processo de Machine Learning.

### Fluxo do Pipeline

```text
Bronze → Silver → Gold → Treinamento
```

### Etapas realizadas

- Leitura dos dados diretamente do MinIO na camada Bronze
- Consolidação dos arquivos CSV em um único dataset
- Tratamento e limpeza dos dados
- Engenharia de features (extração de hora, minuto, dia da semana e mês)
- Geração da camada Silver com dados tratados
- Seleção de variáveis numéricas e preparação final dos dados
- Geração da camada Gold com dados prontos para Machine Learning
- Separação dos dados em treino e teste
- Treinamento de modelo de regressão com Random Forest
- Avaliação com métricas MAE e R²
- Registro de experimentos utilizando MLflow

### Tecnologias utilizadas na Sprint 4

- Python
- pandas
- numpy
- scikit-learn
- MinIO
- MLflow

### Resultado

Foi estruturado um pipeline de dados integrando as camadas Bronze, Silver e Gold ao treinamento do modelo, garantindo organização, rastreabilidade e base para evolução da plataforma.

**Evidência da Sprint 4:** pipeline funcional com leitura da Bronze, geração de Silver e Gold, treinamento do modelo e registro de métricas e artefatos no MLflow.

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

## 3. Executar treinamento do modelo

```bash
python scripts/train_model.py
```

---

# Serviços da Infraestrutura

## PostgreSQL
Responsável por metadados e suporte à arquitetura da aplicação.

## MinIO
Responsável pelo armazenamento dos dados no Data Lake, organizado em Bronze, Silver e Gold.

## Ollama
Responsável pela camada de modelo local utilizada na arquitetura do projeto.

## MLflow
Responsável pelo rastreamento de parâmetros, métricas e artefatos dos experimentos.

---

# Evidências da AC1

A AC1 contempla principalmente as entregas até a Sprint 4.  
No estado atual do projeto, as seguintes evidências podem ser identificadas:

- **Sprint 1:** definição do produto, domínio, empresa fictícia, problema, requisitos, backlog e papéis Scrum
- **Sprint 2:** arquitetura definida e infraestrutura inicial com Docker Compose
- **Sprint 3:** organização do Data Lake com arquitetura Medallion e separação entre Bronze, Silver e Gold
- **Sprint 4:** pipeline de dados integrado ao treinamento do modelo com rastreamento no MLflow

---

# Próximos Passos

As próximas etapas do projeto envolvem a evolução da plataforma para:

- pipeline de embeddings
- armazenamento vetorial
- construção do fluxo RAG
- integração completa entre backend, LLM e recuperação de contexto
- interface de consulta ao usuário

---

# Documento complementar

Para resumo das evidências da AC1, consulte: `docs/ac1.md`

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