# Swiss Regulatory Advisor

Swiss Regulatory Advisor is a FastAPI-based RAG application built for a finance compliance. It ingests regulatory PDF documents over AWS, stores their extracted content as vectors in Qdrant, and answers compliance questions with Gemini using only the uploaded document context.

The project also includes a Streamlit frontend for interacting with the system through a simple portfolio-friendly UI.

## Deployment

The backend is designed to be deployed on Render as a FastAPI web service. Render exposes the API endpoints used by the AWS ingestion pipeline and by the Streamlit frontend.

Main API endpoints:

```text
POST /upload
POST /query
GET /health
```

The Streamlit frontend can be deployed separately or run locally as the user-facing interface. It sends user questions to the FastAPI `/query` endpoint and displays the generated answer with sources.

## Upload Flow

PDF ingestion is automated through AWS:

```text
PDF is uploaded to S3
    -> S3 ObjectCreated event triggers AWS Lambda
    -> Lambda reads the new PDF from S3
    -> Lambda sends the file to the Render API upload endpoint /upload
    -> FastAPI accepts the file and starts processing
    -> PDF text is extracted, chunked, embedded, and stored in Qdrant
```

This keeps the app focused on processing and retrieval. S3 detects new files, Lambda forwards them, and the Render-hosted API handles ingestion into the RAG pipeline.

## RAG Flow

1. A PDF is sent to the FastAPI `/upload` endpoint.
2. The app extracts readable text from the PDF.
3. The text is split into smaller overlapping chunks.
4. Gemini embeddings are generated for each chunk.
5. The chunks and metadata are stored in Qdrant.
6. Users ask questions through the Streamlit frontend.
7. Streamlit sends the question to the FastAPI `/query` endpoint.
8. The backend searches Qdrant for relevant chunks and generates a grounded answer with Gemini.

## Local Development

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set the required values in `.env`:

```text
GEMINI_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
COLLECTION_NAME=swiss_compliance_documents
```

Run the FastAPI backend:

```powershell
uvicorn src.main:app --reload
```

Run the Streamlit frontend:

```powershell
streamlit run src/frontend.py
```

Run tests:

```powershell
pytest
```

## Tech Stack

- FastAPI backend
- Streamlit frontend
- Render deployment
- AWS S3
- AWS Lambda
- Qdrant vector database
- Gemini generation and embeddings
- pypdf
- LangChain Text Splitters
