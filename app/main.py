from fastapi import FastAPI

app = FastAPI(
    title="MediFlow API",
    description="Clinical Workflow Intelligence Platform",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "MediFlow"}