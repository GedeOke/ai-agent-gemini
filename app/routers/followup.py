import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import dependencies
from app.models.schemas import FollowUpRequest
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/schedule")
async def schedule_followup(payload: FollowUpRequest, _: ApiKeyDep) -> dict:
    try:
        await dependencies.followup_service.schedule(payload)
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to schedule follow-up")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule follow-up",
        ) from exc


@router.get("/pending")
async def list_followups(_: ApiKeyDep) -> list[FollowUpRequest]:
    return await dependencies.followup_service.list_pending()
