from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from src.services.document_service import process_regulatory_document
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


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "environment": settings.ENV,
        "project": settings.PROJECT_NAME
    }


from fastapi import FastAPI, UploadFile, File, BackgroundTasks
import shutil
import os

app = FastAPI()


# Move your heavy extraction/vector embedding code into a standalone helper function
def process_pdf_in_background(file_path: str):
    try:
        print(f"Starting heavy background RAG ingestion pipeline for: {file_path}")

        # 1. READ/EXTRACT TEXT FROM PDF HERE
        # 2. CHUNK TEXT HERE
        # 3. GENERATE EMBEDDINGS & SAVE TO QDRANT HERE

        print(f"Successfully finished embedding pipeline for {file_path}")
    except Exception as e:
        print(f"Background processing failed: {str(e)}")
    finally:
        # Clean up the temp file after processing is complete
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. Create a local temporary path copy of the incoming S3 file stream
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Handoff the file path to the background worker thread
    background_tasks.add_task(process_pdf_in_background, temp_file_path)

    # 3. Instantly respond to AWS Lambda with success so the execution closes out
    return {
        "status": "Accepted",
        "message": f"File {file.filename} received. Processing started in background."
    }

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