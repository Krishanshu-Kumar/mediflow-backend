import logging
import uuid
from datetime import datetime, timezone

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

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("mediflow")

app = FastAPI(
    title="MediFlow API",
    description="Clinical Workflow Intelligence Platform",
    version="1.0.0"
)


# ---------------------------------------------------------------------------
# Standard error response builder
# ---------------------------------------------------------------------------
def build_error_response(request: Request, status_code: int, message, log_level: str = "error"):
    """
    Builds a standardized error JSON body:
    { id, message, status_code, token, success }
    Also logs the error server-side with the same id/token so you can
    correlate a client-visible error with what's in your logs.
    """
    error_id = str(uuid.uuid4())
    token = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    log_fn = getattr(logger, log_level, logger.error)
    log_fn(
        f"error_id={error_id} token={token} path={request.method} {request.url.path} "
        f"status={status_code} message={message}"
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "id": error_id,
            "message": message,
            "status_code": status_code,
            "token": token,
            "success": False,
        }
    )


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # Log the real DB error internally (with traceback), but don't leak it to the client
    logger.exception(f"IntegrityError on {request.method} {request.url.path}")
    return build_error_response(
        request,
        status_code=400,
        message="A database integrity error occurred. Please check your input and try again.",
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return build_error_response(
        request,
        status_code=exc.status_code,
        message=exc.detail,
        log_level="warning",  # expected errors (404, 401, etc.) — don't need full "error" noise
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return build_error_response(
        request,
        status_code=422,
        message=exc.errors(),
        log_level="warning",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Full traceback goes to logs; client only sees a generic message
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return build_error_response(
        request,
        status_code=500,
        message="Internal server error. Please try again later.",
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
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