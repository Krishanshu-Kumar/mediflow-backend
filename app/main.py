from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError

from app.api import tenant_api
from app.api import role_api
from app.api.Settings import master_codes as master_code_api
from app.api import auth_api
from app.api import user_api

app = FastAPI(
    title="MediFlow API",
    description="Clinical Workflow Intelligence Platform",
    version="1.0.0"
)


# Exception Handlers

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # Try to extract the database driver's error message, or fallback to the full exception string
    err_msg = str(exc.orig) if hasattr(exc, "orig") and exc.orig else str(exc)
    return JSONResponse(
        status_code=400,
        content={"detail": f"Database integrity error: {err_msg}"}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # If the exception is a standard HTTPException, preserve its status code and message
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # If the exception is a validation error, preserve its 422 status code and detail list
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )
    
    # For any other unhandled server error, return a descriptive 500 error
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error ({exc.__class__.__name__}): {str(exc)}"
        }
    )


# Routers
app.include_router(tenant_api.router)
app.include_router(role_api.router)
app.include_router(master_code_api.router)
app.include_router(auth_api.router)
app.include_router(user_api.router)



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