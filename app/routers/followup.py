import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import dependencies
from app.db import get_session
from app.models.schemas import FollowUpRequest
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/schedule")
async def schedule_followup(
    payload: FollowUpRequest,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if tenant_key not in ("global", "open") and payload.tenant_id != tenant_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant mismatch")
    tenant_settings = await dependencies.tenant_service.get(session, payload.tenant_id)
    if not tenant_settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant not found")
    try:
        await dependencies.followup_service.schedule(session, payload)
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to schedule follow-up")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule follow-up",
        ) from exc


@router.get("/pending")
async def list_followups(
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> list[FollowUpRequest]:
    if tenant_key in ("global", "open"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id header required")
    tenant_settings = await dependencies.tenant_service.get(session, tenant_key)
    if not tenant_settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant not found")
    return await dependencies.followup_service.list_pending(session, tenant_key)
