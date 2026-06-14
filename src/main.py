from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from contextlib import asynccontextmanager
# from src.database.mail_connection import BaseMail, engine_mail
from src.exception_handler import register_exception_handlers
from src.routes.otp import router as otp_router
from src.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Dropping and recreating all tables...")
    # BaseMail.metadata.drop_all(bind=engine_mail)
    # BaseMail.metadata.create_all(bind=engine_mail)
    yield
    print("Shutting down app...")


app = FastAPI(title="Mail Service", lifespan=lifespan)
app.include_router(otp_router, prefix="/otp")
app.include_router(auth_router, prefix="/auth")

register_exception_handlers(app)

origins = [
    "http://localhost:8000",
]
custom_headers = [
    "X-User-Id",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "DELETE", "PUT", "UPDATE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=custom_headers,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error['loc'])
        msg = error['msg']
        errors.append({
            "field": field,
            "message": msg,
            "type": error['type']
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "errors": errors,
            "message": "Validation failed for one or more fields"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": "HTTP Exception occurred",
            "status_code": exc.status_code,
        },
    )


@app.get("/")
def health_check(request: Request):
    return JSONResponse(
        content={
            "status": "Mail Service is running"
        }
    )


@app.get("/test")
def health_check(request: Request):
    return JSONResponse(
        content={
            "status": "ok"
        }
    )
