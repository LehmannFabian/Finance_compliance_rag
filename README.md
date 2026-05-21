# Swiss Regulatory Advisor

FastAPI-based starter project for a Swiss regulatory RAG assistant.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Run

```powershell
uvicorn src.main:app --reload
```

## Test

```powershell
pytest
```
