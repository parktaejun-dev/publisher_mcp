from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, ForeignKey, Text, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    stored_filename = Column(Text, nullable=False)
    original_filename = Column(Text, nullable=False)
    content_type = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    sha256 = Column(Text, nullable=False, unique=True)
    media_owner = Column(Text, nullable=False)
    media_name = Column(Text, nullable=False)
    doc_type = Column(Text, nullable=False)
    doc_date = Column(Date, nullable=True)
    tags = Column(ARRAY(Text), nullable=False, server_default=text("'{}'"))
    confidentiality = Column(Text, nullable=False, server_default=text("'internal'"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class IngestJob(Base):
    __tablename__ = "ingest_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    engine = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    attempt = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    document = relationship("Document")

class MediaRecordDraft(Base):
    __tablename__ = "media_records_draft"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    engine = Column(Text, nullable=False)
    raw_json = Column(JSONB, nullable=False)
    validation_report = Column(JSONB, nullable=False)
    status = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("Document")

class MediaRecord(Base):
    __tablename__ = "media_records"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    draft_id = Column(UUID(as_uuid=True), ForeignKey("media_records_draft.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    media_owner = Column(Text, nullable=True)
    media_name = Column(Text, nullable=True)
    media_type = Column(Text, nullable=True)
    product_name = Column(Text, nullable=True)
    pricing_model = Column(Text, nullable=True)
    price_text = Column(Text, nullable=True)
    min_budget_text = Column(Text, nullable=True)
    targeting_text = Column(Text, nullable=True)
    specs_text = Column(Text, nullable=True)
    kpi_text = Column(Text, nullable=True)
    sales_contact = Column(Text, nullable=True)
    valid_until = Column(Date, nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    draft = relationship("MediaRecordDraft")
    document = relationship("Document")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    record_kind = Column(Text, nullable=False) # 'draft' or 'approved'
    record_id = Column(UUID(as_uuid=True), nullable=False)
    field = Column(Text, nullable=False)
    quote = Column(Text, nullable=False)
    page = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
