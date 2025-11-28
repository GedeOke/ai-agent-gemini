import logging
from typing import List

from app.models.schemas import FollowUpRequest

logger = logging.getLogger(__name__)


class FollowUpService:
    """
    Placeholder scheduler; swap with queue/worker later.
    """

    def __init__(self) -> None:
        self._queue: List[FollowUpRequest] = []

    async def schedule(self, request: FollowUpRequest) -> None:
        try:
            self._queue.append(request)
            logger.info("Follow-up scheduled for user=%s at %s", request.user_id, request.scheduled_at)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to schedule follow-up")
            raise exc

    async def list_pending(self) -> List[FollowUpRequest]:
        return list(self._queue)
