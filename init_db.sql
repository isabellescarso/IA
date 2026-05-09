-- ============================================================
-- Inicialização do banco relacional RAG CGMacros
-- ============================================================

-- Modelos LLM
CREATE TABLE IF NOT EXISTS llm_models (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(64) NOT NULL UNIQUE,
    provider   VARCHAR(32) NOT NULL DEFAULT 'ollama',
    is_active  BOOLEAN     NOT NULL DEFAULT TRUE,
    is_default BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_llm_models_single_default
    ON llm_models (is_default)
    WHERE is_default = TRUE;

CREATE INDEX IF NOT EXISTS idx_llm_models_active
    ON llm_models (is_active);

INSERT INTO llm_models (name, provider, is_active, is_default)
VALUES
    ('llama3.2',         'ollama', TRUE, TRUE),
    ('mistral',          'ollama', TRUE, FALSE),
    ('nomic-embed-text', 'ollama', TRUE, FALSE)
ON CONFLICT (name) DO NOTHING;

-- Pacientes
CREATE TABLE IF NOT EXISTS patients (
    id            SERIAL PRIMARY KEY,
    patient_id    VARCHAR(64) NOT NULL UNIQUE,
    total_vectors INTEGER,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO patients (patient_id, total_vectors)
VALUES
    ('CGMacros-012', 0),
    ('CGMacros-039', 0)
ON CONFLICT (patient_id) DO NOTHING;

-- Logs de consultas
CREATE TABLE IF NOT EXISTS ask_logs (
    id         SERIAL PRIMARY KEY,
    question   TEXT        NOT NULL,
    answer     TEXT        NOT NULL,
    model_id   INTEGER     REFERENCES llm_models (id) ON DELETE SET NULL,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ask_logs_created_at ON ask_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ask_logs_model_id   ON ask_logs (model_id);

-- Experimentos de prompts
CREATE TABLE IF NOT EXISTS prompt_experiments (
    id          SERIAL PRIMARY KEY,
    prompt_hash VARCHAR(64) NOT NULL,
    question    TEXT        NOT NULL,
    model_id    INTEGER     REFERENCES llm_models (id) ON DELETE SET NULL,
    score       FLOAT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prompt_experiments_model_id
    ON prompt_experiments (model_id);