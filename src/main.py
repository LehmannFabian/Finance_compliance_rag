import os
import shutil
import urllib.request
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from pypdf import PdfReader
from src.services.rag_service import RAGService
from src.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Secure FINMA and Swiss legal regulatory parsing engine using Gemini RAG."
)

rag_service = RAGService()


class QueryRequest(BaseModel):
    question: str

class S3WebhookPayload(BaseModel):
    filename: str
    download_url: str


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "environment": settings.ENV,
        "project": settings.PROJECT_NAME
    }



def process_pdf_in_background(file_path: str):
    try:
        print(f"Starting heavy background RAG ingestion pipeline for: {file_path}")

        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        chunk_size = 1000
        chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]

        print(f"DEBUG: {len(chunks)} Chunks were created.")

        if chunks:
            filename = os.path.basename(file_path)
            rag_service.vector_db.save_chunks(filename, chunks)
        else:
            print("WARNUNG: Kein Text im PDF gefunden!")

        print(f"Successfully finished embedding pipeline for {file_path}")

    except Exception as e:
        print(f"Background processing failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/webhook/s3")
async def s3_file_webhook(payload: S3WebhookPayload, background_tasks: BackgroundTasks):
    temp_file_path = f"/tmp/{payload.filename}"

    try:
        with urllib.request.urlopen(payload.download_url) as response, open(temp_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        background_tasks.add_task(process_pdf_in_background, temp_file_path)

        return {"status": "Accepted", "message": f"Processing {payload.filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch file from S3: {str(e)}")

@app.post("/query")
def query_regulatory_knowledge(request: QueryRequest):
    """
    Accepts an input question, initiates vector lookups against our document database,
    and generates grounded answers via Gemini 2.5 Flash.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="The question field cannot be left blank.")

    # Execute the RAG pipeline
    result = rag_service.answer_question(request.question)
    return result
