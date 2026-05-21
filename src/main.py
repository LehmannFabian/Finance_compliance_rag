from pydantic import BaseModel
import urllib.request
import shutil
import os


# Define the incoming structure from Lambda
class S3WebhookPayload(BaseModel):
    filename: str
    download_url: str


def process_pdf_in_background(file_path: str):
    try:
        print(f"Starting heavy background RAG ingestion pipeline for: {file_path}")
        # Your text extraction, chunking, and Qdrant logic runs here...
        print(f"Successfully finished embedding pipeline for {file_path}")
    except Exception as e:
        print(f"Background processing failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/webhook/s3")
async def s3_file_webhook(payload: S3WebhookPayload, background_tasks: BackgroundTasks):
    temp_file_path = f"temp_{payload.filename}"

    try:
        # Securely stream the file components directly down from the S3 link
        with urllib.request.urlopen(payload.download_url) as response, open(temp_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        # Hand the downloaded file off to your background threads safely
        background_tasks.add_task(process_pdf_in_background, temp_file_path)

        return {"status": "Accepted", "message": f"Processing {payload.filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch file from S3: {str(e)}")