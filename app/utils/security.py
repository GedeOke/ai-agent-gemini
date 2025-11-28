import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import settings
from app.db import get_session
from app.models.db_models import Tenant

logger = logging.getLogger(__name__)


async def verify_api_key(
    session: Annotated[AsyncSession, Depends(get_session)],
    x_api_key: Annotated[str | None, Header(convert_underscores=False)] = None,
    x_tenant_id: Annotated[str | None, Header(convert_underscores=False)] = None,
) -> str:
    """
    API key gate with per-tenant support.
    - If X-Tenant-Id is provided, validate against tenant.api_key.
    - Otherwise fall back to global API_KEY from settings.
    """
    # Prefer tenant-scoped key
    if x_tenant_id:
        result = await session.execute(select(Tenant).where(Tenant.tenant_id == x_tenant_id))
        tenant_row = result.scalar_one_or_none()
        if not tenant_row:
            logger.warning("Tenant not found: %s", x_tenant_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        if not x_api_key or x_api_key != tenant_row.api_key:
            logger.warning("Invalid tenant API key for tenant=%s", x_tenant_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        return x_tenant_id

    # Fallback to global key
    if settings.api_key:
        if not x_api_key or x_api_key != settings.api_key:
            logger.warning("Unauthorized request rejected (global key)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )
        return "global"

    # If nothing configured, allow (dev mode)
    logger.warning("API key check bypassed (no key configured)")
    return "open"


ApiKeyDep = Annotated[str, Depends(verify_api_key)]
