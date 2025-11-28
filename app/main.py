import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status

from app.config import settings
from app.routers import chat, followup, kb, tenant
from app.utils.logging import configure_logging

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s %s: %s", request.method, request.url, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(kb.router, prefix="/kb", tags=["knowledge"])
    app.include_router(tenant.router, prefix="/tenants", tags=["tenant"])
    app.include_router(followup.router, prefix="/followup", tags=["followup"])

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
