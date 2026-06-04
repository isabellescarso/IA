# Tema/Objetivo

**Plataforma RAG Enterprise com Governança de Dados (local)**

Construir uma plataforma completa de Retrieval-Augmented Generation (RAG) para uma empresa fictícia, utilizando:
• Governança com Arquitetura Medallion (Bronze / Silver / Gold)
• Armazenamento em Data Lake (MinIO)
• Banco relacional (PostgreSQL)
• Banco vetorial (Milvus)
• Experiment tracking (MLflow)
• Inferência com LLM local (Ollama)
• API (FastAPI)
• Interface (Gradio ou frontend simples)
• Tudo containerizado com Docker Compose
• Automação via Makefile
• Gerenciado com metodologia -> Scrum

---

**Entregáveis Obrigatórios**

1. Docker Compose funcional
2. Makefile com comandos padronizados
3. API documentada (Contrato da app)
4. RAG funcionando ponta a ponta
5. Documentação arquitetural
6. Demonstração final
7. Sprint backlog documentado
8. Justificativa das decisões técnicas

---

Sprint 1 - Definição do Produto

• Escolha do domínio
• Definição da empresa fictícia
• Definição do problema de negócio
• Levantamento de requisitos
• Definição dos papéis Scrum
Entregável:
• Product Backlog inicial

---

Sprint 2 - Arquitetura e Infraestrutura Base

• Definição da arquitetura geral
• Desenho da arquitetura
• Setup inicial Docker Compose
• Subir MinIO e PostgreSQL
Entregável:
• Diagrama arquitetural
• Compose inicial funcional

---

Sprint 3 - Governança e Medallion

• Estruturar Bronze / Silver / Gold
• Pipeline de ingestão
• Versionamento no MinIO

Entregável:
• Dados organizados nas 3 camadas
• Documentação de governança

---

Sprint 4 - Modelagem e Treinamento de Modelos (ML + MLflow) (AC1)

- Definição do problema de ML (ex: classificação, regressão, série
  temporal)
- Seleção de modelos (ex: Linear, Logistica, LSTM, XGBoost, TCN,
  etc.)
- Criação dos scripts de treinamento 
- Integração com MLflow (tracking de experimentos)
  Entregável:
  • Pipeline de treino funcional
  • Experimentos registrados no MLflow

---

Sprint 5 - Pipeline de Embeddings

• Setup Milvus
• Integração com Ollama
• Geração de embeddings
• Indexação vetorial

Entregável:
• Index funcional
• Processo automatizado

---

Sprint 6 - Construção do RAG Core

• Implementar busca vetorial
• Construção de prompt
• Integração com LLM
Entregável:
• RAG funcionando via script

---

Sprint 7 - API (AC2)

• Construção do FastAPI
• Endpoints:
/query
/metadata
• Validação de input/output

Entregável:
• API documentada

---

Sprint 8 - Interface

• Implementar Gradio
	ou
• Criar frontend simples

Entregável:
• Interface funcional

---

Sprint 9 - MLflow e Avaliação

- Tracking de experimentos
- Comparação de prompts
- Métricas de avaliação (ex: relevância)

Entregável:
• Experimentos registrados

---

Sprint 10 - Automação

• Criar Makefile
make up
make down
….
• Testes básicos
Entregável:
• Pipeline totalmente automatizado

---

Sprint 11 e Sprint 12 - Validação, Avaliação e Preparação do Pitch (10 min) (AF)

Entregável:
• Sistema robusto
• Video Pitch (será apresentado no dia de Lab. na semana da AF)

---

**Critérios de Avaliação**

| Critério            | Peso |
| ------------------- | ---- |
| Arquitetura         | 20%  |
| Governança de dados | 15%  |
| Qualidade do RAG    | 20%  |
| Infraestrutura      | 15%  |
| Documentação        | 15%  |
| Apresentação final  | 15%  |