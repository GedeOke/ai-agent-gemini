import logging
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Tenant
from app.models.schemas import TenantSettings

logger = logging.getLogger(__name__)


class TenantService:
    async def get(self, session: AsyncSession, tenant_id: str) -> TenantSettings | None:
        result = await session.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None
        return TenantSettings(
            tenant_id=tenant.tenant_id,
            api_key=tenant.api_key,
            persona=tenant.persona,
            sop=tenant.sop,
            working_hours=tenant.working_hours,
            timezone=tenant.timezone,
            followup_enabled=tenant.followup_enabled,
            followup_interval_minutes=int(tenant.followup_interval_minutes),
        )

    async def upsert(self, session: AsyncSession, payload: TenantSettings) -> TenantSettings:
        result = await session.execute(select(Tenant).where(Tenant.tenant_id == payload.tenant_id))
        tenant = result.scalar_one_or_none()
        try:
            if tenant:
                tenant.api_key = payload.api_key or tenant.api_key
                tenant.persona = payload.persona.model_dump()
                tenant.sop = payload.sop.model_dump()
                tenant.working_hours = payload.working_hours
                tenant.timezone = payload.timezone
                tenant.followup_enabled = payload.followup_enabled
                tenant.followup_interval_minutes = payload.followup_interval_minutes
            else:
                session.add(
                    Tenant(
                        tenant_id=payload.tenant_id,
                        api_key=payload.api_key or secrets.token_hex(16),
                        persona=payload.persona.model_dump(),
                        sop=payload.sop.model_dump(),
                        working_hours=payload.working_hours,
                        timezone=payload.timezone,
                        followup_enabled=payload.followup_enabled,
                        followup_interval_minutes=payload.followup_interval_minutes,
                    )
                )
            await session.commit()
            logger.info("Tenant settings upserted for %s", payload.tenant_id)
            return await self.get(session, payload.tenant_id)  # type: ignore
        except Exception as exc:  # pragma: no cover - defensive
            await session.rollback()
            logger.exception("Failed to upsert tenant settings")
            raise exc
