from fastapi import FastAPI

from app.api import tenant_api
from app.api import role_api

app = FastAPI(
    title="MediFlow API",
    description="Clinical Workflow Intelligence Platform",
    version="1.0.0"
)

# Routers
app.include_router(tenant_api.router)
app.include_router(role_api.router)


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "service": "MediFlow"
    }


@app.get("/patients/{patient_id}", tags=["Demo"])
def get_patient(patient_id: str):
    return {
        "patient_id": patient_id,
        "first_name": "Janet",
        "last_name": "Doe",
        "date_of_birth": "1990-04-15",
        "mrn": "MRN-00123",
        "status": "Inactive"
    }