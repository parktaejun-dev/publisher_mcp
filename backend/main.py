from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="KOBACO Ad Data Layer")

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to KOBACO Ad Data Layer API"}

# Include routers
from backend.api import documents, jobs, records, import_json
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(records.router, prefix="/api/records", tags=["records"])
app.include_router(import_json.router, prefix="/api/import-json", tags=["import"])
