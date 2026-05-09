-- ============================================================
-- Inicialização do banco relacional RAG CGMacros
-- Executado automaticamente pelo PostgreSQL no primeiro start
-- ============================================================

-- Tabela de logs de consultas feitas pelo usuário via /ask
CREATE TABLE IF NOT EXISTS ask_logs (
    id          SERIAL PRIMARY KEY,
    question    TEXT        NOT NULL,
    answer      TEXT        NOT NULL,
    model_used  VARCHAR(64) NOT NULL DEFAULT 'llama3.2',
    latency_ms  INTEGER,                          -- tempo de resposta em ms
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabela de metadados dos pacientes disponíveis no sistema
CREATE TABLE IF NOT EXISTS patients (
    id          SERIAL PRIMARY KEY,
    patient_id  VARCHAR(64) NOT NULL UNIQUE,      -- ex: CGMacros-012
    total_vectors INTEGER,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Inserir pacientes iniciais
INSERT INTO patients (patient_id, total_vectors)
VALUES
    ('CGMacros-012', 0),
    ('CGMacros-039', 0)
ON CONFLICT (patient_id) DO NOTHING;

-- Tabela de experimentos de prompts (complementa o MLflow)
CREATE TABLE IF NOT EXISTS prompt_experiments (
    id           SERIAL PRIMARY KEY,
    prompt_hash  VARCHAR(64)  NOT NULL,           -- hash do prompt para deduplicação
    question     TEXT         NOT NULL,
    model_used   VARCHAR(64)  NOT NULL,
    score        FLOAT,                           -- métrica de relevância (0–1)
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para buscas frequentes
CREATE INDEX IF NOT EXISTS idx_ask_logs_created_at   ON ask_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ask_logs_model        ON ask_logs (model_used);
CREATE INDEX IF NOT EXISTS idx_prompt_experiments_model ON prompt_experiments (model_used);