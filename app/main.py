from fastapi import FastAPI
from app.api import tenant

# ✅ First create app
app = FastAPI(
    title="MediFlow API",
    description="Clinical Workflow Intelligence Platform",
    version="1.0.0"
)

# ✅ Then include router
app.include_router(tenant.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "MediFlow"}


@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    return {
        "patient_id": patient_id,
        "first_name": "Janet",
        "last_name": "Doe",
        "date_of_birth": "1990-04-15",
        "mrn": "MRN-00123",
        "status": "Inactive"
    }