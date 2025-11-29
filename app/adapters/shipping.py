import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ShippingClient:
    """
    Placeholder shipping adapter. Replace with real courier API integration.
    """

    async def quote(self, origin: str, destination: str, weight_kg: float) -> Dict[str, str | float]:
        logger.info("Fetching shipping quote origin=%s destination=%s weight=%s", origin, destination, weight_kg)
        try:
            # TODO: replace with actual courier API call
            return {"provider": "mock", "price": 25000, "currency": "IDR", "eta_days": 2}
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Shipping quote failed")
            raise
