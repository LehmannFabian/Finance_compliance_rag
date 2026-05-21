from fastapi import FastAPI


app = FastAPI(title="Swiss Regulatory Advisor")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
