import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import dependencies
from app.db import get_session
from app.models.schemas import SopState
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/state", response_model=SopState)
async def get_state(
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
    contact_id: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
) -> SopState:
    if tenant_key in ("global", "open"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id header required")
    return await dependencies.sop_state_service.get_state(session, tenant_key, contact_id, user_id)


@router.put("/state", response_model=SopState)
async def set_state(
    payload: SopState,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> SopState:
    if tenant_key not in ("global", "open") and payload.tenant_id != tenant_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant mismatch")
    try:
        return await dependencies.sop_state_service.set_state(session, payload)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to set SOP state")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set SOP state",
        ) from exc
