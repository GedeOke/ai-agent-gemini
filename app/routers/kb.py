import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import dependencies
from app.db import get_session
from app.models.schemas import KnowledgeUpsertRequest
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upsert")
async def upsert_kb(
    payload: KnowledgeUpsertRequest,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if tenant_key not in ("global", "open") and payload.tenant_id != tenant_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant mismatch")
    tenant_settings = await dependencies.tenant_service.get(session, payload.tenant_id)
    if not tenant_settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant not found")
    try:
        await dependencies.rag_service.upsert(session, payload.tenant_id, payload.items)
        return {"status": "ok", "count": len(payload.items)}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("KB upsert failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upsert knowledge base",
        ) from exc
