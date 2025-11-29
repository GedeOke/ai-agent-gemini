import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import dependencies
from app.db import get_session
from app.models.schemas import ChatMessage, Contact, ContactCreate
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=Contact)
async def upsert_contact(
    payload: ContactCreate,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> Contact:
    if tenant_key not in ("global", "open") and payload.tenant_id != tenant_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant mismatch")
    try:
        return await dependencies.contact_service.upsert(session, payload)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to upsert contact")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upsert contact",
        ) from exc


@router.get("", response_model=list[Contact])
async def list_contacts(
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, le=200),
) -> list[Contact]:
    if tenant_key in ("global", "open"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id header required")
    return await dependencies.contact_service.list(session, tenant_key, limit=limit)


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: str,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> Contact:
    if tenant_key in ("global", "open"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id header required")
    contact = await dependencies.contact_service.get(session, contact_id, tenant_key)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


@router.post("/logs")
async def log_message(
    payload: ChatMessage,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if tenant_key not in ("global", "open") and payload.tenant_id != tenant_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant mismatch")
    try:
        await dependencies.contact_service.log_message(session, payload)
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to log message")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log message",
        ) from exc


@router.get("/logs")
async def list_history(
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
    contact_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    if tenant_key in ("global", "open"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id header required")
    return await dependencies.contact_service.history(session, tenant_key, contact_id, limit)
