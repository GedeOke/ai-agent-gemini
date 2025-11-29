import asyncio
import contextlib
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import FollowUpModel

logger = logging.getLogger(__name__)


class FollowUpScheduler:
    """
    Simple polling scheduler. In production replace with queue/worker (Redis/Celery/RQ).
    """

    def __init__(self, poll_interval_seconds: int = 15) -> None:
        self.poll_interval_seconds = poll_interval_seconds
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self, session_factory) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run(session_factory))
        logger.info("Follow-up scheduler started (interval=%ss)", self.poll_interval_seconds)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(Exception):
                await self._task

    async def _run(self, session_factory) -> None:
        while self._running:
            try:
                async with session_factory() as session:
                    await self._process_due(session)
            except Exception:  # pragma: no cover - defensive
                logger.exception("Scheduler tick failed")
            await asyncio.sleep(self.poll_interval_seconds)

    async def _process_due(self, session: AsyncSession) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(FollowUpModel)
            .where(
                FollowUpModel.scheduled_at <= now,
                FollowUpModel.status == "pending",
            )
            .limit(20)
        )
        result = await session.execute(stmt)
        due_items = result.scalars().all()
        if not due_items:
            return
        for item in due_items:
            try:
                # TODO: integrate actual send via channel adapter
                logger.info("Dispatching follow-up id=%s tenant=%s user=%s", item.id, item.tenant_id, item.user_id)
                item.status = "sent"
                item.sent_at = now
                item.last_error = None
            except Exception as exc:  # pragma: no cover - defensive
                item.status = "failed"
                item.last_error = str(exc)
        await session.commit()
