import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import FollowUpModel
from app.models.schemas import FollowUpRequest

logger = logging.getLogger(__name__)


class FollowUpService:
    """
    DB-backed placeholder; swap with queue/worker later.
    """

    async def schedule(self, session: AsyncSession, request: FollowUpRequest) -> None:
        try:
            session.add(
                FollowUpModel(
                    tenant_id=request.tenant_id,
                    user_id=request.user_id,
                    reason=request.reason,
                    scheduled_at=request.scheduled_at,
                    channel=request.channel,
                    meta=request.metadata,
                    status="pending",
                )
            )
            await session.commit()
            logger.info("Follow-up scheduled for tenant=%s user=%s at %s", request.tenant_id, request.user_id, request.scheduled_at)
        except Exception as exc:  # pragma: no cover - defensive
            await session.rollback()
            logger.exception("Failed to schedule follow-up")
            raise exc

    async def list_pending(self, session: AsyncSession, tenant_id: str) -> List[FollowUpRequest]:
        result = await session.execute(
            select(FollowUpModel).where(FollowUpModel.tenant_id == tenant_id).order_by(FollowUpModel.scheduled_at)
        )
        rows = result.scalars().all()
        return [
            FollowUpRequest(
                tenant_id=row.tenant_id,
                user_id=row.user_id,
                reason=row.reason,
                scheduled_at=row.scheduled_at,
                channel=row.channel,
                metadata=row.meta or {},
            )
            for row in rows
        ]

    async def list_by_status(self, session: AsyncSession, tenant_id: str, status: Optional[str] = None) -> List[FollowUpModel]:
        stmt = select(FollowUpModel).where(FollowUpModel.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(FollowUpModel.status == status)
        result = await session.execute(stmt.order_by(FollowUpModel.scheduled_at))
        return result.scalars().all()
