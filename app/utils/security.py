import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from starlette import status

from app.config import settings

logger = logging.getLogger(__name__)


async def verify_api_key(x_api_key: Annotated[str | None, Header(convert_underscores=False)] = None) -> bool:
    """
    Simple API-key gate. If no key configured, the check is bypassed.
    """
    if settings.api_key:
        if not x_api_key or x_api_key != settings.api_key:
            logger.warning("Unauthorized request rejected")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )
    return True


ApiKeyDep = Annotated[bool, Depends(verify_api_key)]
