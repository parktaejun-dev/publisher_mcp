import time
import os
import traceback
from sqlalchemy.orm import Session
from backend.db.session import SessionLocal
from backend.db.models import IngestJob, Document, MediaRecordDraft, MediaRecord
# from backend.engines import get_engine (dynamic import)

JOB_POLL_INTERVAL = int(os.getenv("JOB_POLL_INTERVAL", "5"))

def process_job_logic(job_id: str):
    """
    Performs the heavy lifting of parsing and saving drafts.
    This runs AFTER the job has been marked 'processing'.
    """
    db = SessionLocal()
    try:
        job = db.query(IngestJob).filter(IngestJob.id == job_id).first()
        if not job:
            return # Should not happen

        # 1. Get Document
        doc = db.query(Document).filter(Document.id == job.document_id).first()
        if not doc:
            raise ValueError(f"Document {job.document_id} not found")

        # 2. Get Engine
        from backend.engines.base import get_engine
        engine_instance = get_engine(job.engine)
        if not engine_instance:
            raise ValueError(f"Engine {job.engine} not found")

        # 3. Parse
        print(f"Processing job {job.id} for document {doc.id} with engine {job.engine}")
        try:
            parsed_result = engine_instance.parse(doc)
        except Exception as e:
            raise ValueError(f"Engine parsing failed: {e}")

        # 4. Create Draft
        # Ensure raw_json is a dict
        raw_json = parsed_result.raw_json if isinstance(parsed_result.raw_json, dict) else {}

        draft = MediaRecordDraft(
            document_id=doc.id,
            engine=job.engine,
            raw_json=raw_json,
            validation_report=parsed_result.validation_report,
            status=parsed_result.status
        )
        db.add(draft)

        # 5. Update Job Status
        # Map draft status to job status
        if parsed_result.status == "needs_review":
             job.status = "needs_review"
        else:
             job.status = "draft_saved"

        db.commit()
        print(f"Job {job.id} completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Job {job_id} failed logic: {e}")
        traceback.print_exc()
        try:
            # Re-fetch job to update status independently
            job = db.query(IngestJob).filter(IngestJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.last_error = str(e)[:1000]
                db.commit()
        except:
            pass
    finally:
        db.close()

def run_worker():
    print("Worker started...")
    while True:
        job_id_to_process = None

        try:
            db = SessionLocal()
            # Pick a job and mark as processing immediately to release lock but keep it reserved
            job = db.query(IngestJob).filter(IngestJob.status == "queued")\
                    .order_by(IngestJob.created_at.asc())\
                    .with_for_update(skip_locked=True)\
                    .first()

            if job:
                job_id_to_process = job.id
                job.status = "processing"
                job.last_error = None
                db.commit()

            db.close()

        except Exception as e:
            print(f"Worker polling error: {e}")
            time.sleep(1)
            continue

        if job_id_to_process:
            process_job_logic(job_id_to_process)
        else:
            time.sleep(JOB_POLL_INTERVAL)

if __name__ == "__main__":
    run_worker()
