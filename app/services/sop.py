import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import SopStateModel
from app.models.schemas import ChatRequest, SalesSop, SopState

logger = logging.getLogger(__name__)


class SopStateMachine:
    """
    Simple SOP state machine for sales flow.
    Tracks current step based on tags/keywords and advances sequentially.
    """

    def __init__(self) -> None:
        self.keywords = {
            "reach out": ["halo", "hai", "selamat"],
            "keluhan": ["keluhan", "masalah", "complain", "problem"],
            "konsultasi": ["konsultasi", "tanya", "butuh saran"],
            "rekomendasi": ["rekomendasi", "cocok", "produk yang cocok"],
            "harga": ["harga", "biaya", "fee"],
        }

    def current_step_from_text(self, sop: SalesSop, history: ChatRequest) -> Optional[str]:
        if not sop.steps:
            return None
        for msg in reversed(history.messages):
            for step in sop.steps:
                if any(kw in msg.content.lower() for kw in self.keywords.get(step.name.lower(), [])):
                    return step.name
        return None

    def next_step(self, sop: SalesSop, current: Optional[str]) -> Optional[str]:
        if not sop.steps:
            return None
        names = [s.name for s in sop.steps]
        if current is None:
            return names[0]
        if current in names:
            idx = names.index(current)
            if idx + 1 < len(names):
                return names[idx + 1]
        return None

    def sop_hint(self, sop: SalesSop, current: Optional[str]) -> str:
        nxt = self.next_step(sop, current)
        parts = []
        if current:
            parts.append(f"Langkah saat ini: {current}.")
        if nxt:
            parts.append(f"Lanjutkan ke langkah berikut: {nxt}.")
        else:
            parts.append("Langkah akhir tercapai; lakukan closing/penutup.")
        return " ".join(parts)


class SopStateService:
    """
    Persist SOP state per contact/user.
    """

    def __init__(self, machine: SopStateMachine) -> None:
        self.machine = machine

    async def get_state(self, session: AsyncSession, tenant_id: str, contact_id: Optional[str], user_id: Optional[str]) -> SopState:
        stmt = select(SopStateModel).where(SopStateModel.tenant_id == tenant_id)
        if contact_id:
            try:
                cid = uuid.UUID(contact_id)
                stmt = stmt.where(SopStateModel.contact_id == cid)
            except Exception:
                logger.warning("Invalid contact_id for SOP state: %s", contact_id)
        if user_id:
            stmt = stmt.where(SopStateModel.user_id == user_id)
        row = (await session.execute(stmt)).scalar_one_or_none()
        return SopState(
            tenant_id=tenant_id,
            contact_id=str(row.contact_id) if row and row.contact_id else contact_id,
            user_id=row.user_id if row else user_id,
            current_step=row.current_step if row else None,
        )

    async def set_state(self, session: AsyncSession, state: SopState) -> SopState:
        try:
            stmt = select(SopStateModel).where(SopStateModel.tenant_id == state.tenant_id)
            if state.contact_id:
                stmt = stmt.where(SopStateModel.contact_id == uuid.UUID(state.contact_id))
            if state.user_id:
                stmt = stmt.where(SopStateModel.user_id == state.user_id)
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                existing.current_step = state.current_step
            else:
                session.add(
                    SopStateModel(
                        tenant_id=state.tenant_id,
                        contact_id=uuid.UUID(state.contact_id) if state.contact_id else None,
                        user_id=state.user_id,
                        current_step=state.current_step,
                    )
                )
            await session.commit()
            return state
        except Exception as exc:  # pragma: no cover - defensive
            await session.rollback()
            logger.exception("Failed to set SOP state")
            raise exc

    async def update_from_history(self, session: AsyncSession, sop: SalesSop, payload: ChatRequest) -> SopState:
        state = await self.get_state(session, payload.tenant_id, payload.metadata.get("contact_id"), payload.user_id)
        detected = self.machine.current_step_from_text(sop, payload)
        if detected and detected != state.current_step:
            state.current_step = detected
            await self.set_state(session, state)
        if not state.current_step:
            # initialize to first step
            first = sop.steps[0].name if sop.steps else None
            state.current_step = first
            await self.set_state(session, state)
        return state
