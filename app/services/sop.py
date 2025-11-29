import logging
from typing import Optional

from app.models.schemas import ChatRequest, SalesSop

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
            "rekomendasi": ["rekomendasi", "produk yang cocok", "cocok"],
            "harga": ["harga", "biaya", "fee"],
        }

    def current_step(self, sop: SalesSop, history: ChatRequest) -> Optional[str]:
        if not sop.steps:
            return None
        # naive: pick last matched keyword
        for msg in reversed(history.messages):
            for step in sop.steps:
                if any(kw in msg.content.lower() for kw in self.keywords.get(step.name.lower(), [])):
                    return step.name
        # default to first step if none matched
        return sop.steps[0].name

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

    def sop_hint(self, sop: SalesSop, history: ChatRequest) -> str:
        curr = self.current_step(sop, history)
        nxt = self.next_step(sop, curr)
        parts = []
        if curr:
            parts.append(f"Langkah saat ini: {curr}.")
        if nxt:
            parts.append(f"Lanjutkan ke langkah berikut: {nxt}.")
        else:
            parts.append("Langkah akhir tercapai; lakukan closing/penutup.")
        return " ".join(parts)
