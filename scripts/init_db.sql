-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Documents Table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stored_filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    sha256 TEXT NOT NULL,
    media_owner TEXT NOT NULL,
    media_name TEXT NOT NULL,
    doc_type TEXT NOT NULL CHECK (doc_type IN ('media_kit', 'rate_card', 'proposal', 'etc')),
    doc_date DATE,
    tags TEXT[] NOT NULL DEFAULT '{}',
    confidentiality TEXT NOT NULL DEFAULT 'internal' CHECK (confidentiality IN ('public', 'internal', 'restricted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX documents_sha256_idx ON documents(sha256);
CREATE INDEX documents_media_owner_idx ON documents(media_owner);

-- Ingest Jobs Table
CREATE TABLE ingest_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    engine TEXT NOT NULL CHECK (engine IN ('notebooklm', 'user_llm', 'server_native')),
    status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'draft_saved', 'needs_review', 'failed')),
    attempt INT NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX jobs_status_idx ON ingest_jobs(status);
CREATE INDEX jobs_engine_idx ON ingest_jobs(engine);

-- Media Records Draft Table
CREATE TABLE media_records_draft (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    engine TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    validation_report JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft_saved', 'needs_review')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX drafts_document_id_idx ON media_records_draft(document_id);

-- Media Records (Approved) Table
CREATE TABLE media_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES media_records_draft(id),
    document_id UUID NOT NULL REFERENCES documents(id),
    media_owner TEXT,
    media_name TEXT,
    media_type TEXT,
    product_name TEXT,
    pricing_model TEXT,
    price_text TEXT,
    min_budget_text TEXT,
    targeting_text TEXT,
    specs_text TEXT,
    kpi_text TEXT,
    sales_contact TEXT,
    valid_until DATE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX records_media_owner_idx ON media_records(media_owner);
CREATE INDEX records_media_type_idx ON media_records(media_type);

-- Evidence Table
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_kind TEXT NOT NULL CHECK (record_kind IN ('draft', 'approved')),
    record_id UUID NOT NULL,
    field TEXT NOT NULL,
    quote TEXT NOT NULL,
    page INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX evidence_record_idx ON evidence(record_kind, record_id);
