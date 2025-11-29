import logging
from typing import List

from app.models.schemas import ChatRequest, TenantSettings
from app.services.sop import SopStateMachine

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Build structured prompts so instructions, persona, and SOP are consistently applied.
    """

    def __init__(self, sop_machine: SopStateMachine | None = None) -> None:
        self.sop_machine = sop_machine

    def build_chat_prompt(
        self,
        payload: ChatRequest,
        retrieved_context: List[str],
        tenant_settings: TenantSettings,
    ) -> str:
        persona = tenant_settings.persona
        sop_steps = "\n".join(f"{step.order}. {step.description}" for step in tenant_settings.sop.steps)
        sop_hint = ""
        if self.sop_machine:
            sop_hint = self.sop_machine.sop_hint(tenant_settings.sop, payload)
        context_block = "\n".join(retrieved_context) if retrieved_context else "Tidak ada konteks tambahan."

        prompt = (
            f"Peran kamu: AI asisten {persona.persona} yang berbicara dengan gaya: {persona.style_prompt}. "
            f"Tone: {persona.tone}. Bahasa utama: {persona.language}.\n"
            f"Ikuti SOP berikut (urutkan sesuai kebutuhan percakapan):\n{sop_steps if sop_steps else '- Tidak ada SOP khusus.'}\n\n"
            f"Panduan langkah saat ini: {sop_hint}\n\n"
            f"Gunakan konteks pengetahuan bisnis berikut jika relevan:\n{context_block}\n\n"
            f"Percakapan terbaru:\n"
        )

        for msg in payload.messages[-10:]:
            media_note = f" [media: {msg.media_type} {msg.media_url}]" if msg.media_url else ""
            prompt += f"{msg.role.upper()}: {msg.content}{media_note}\n"

        prompt += (
            "\nTugas:\n"
            "- Jawab secara ringkas, jelas, dan empatik.\n"
            "- Jika jawaban panjang, pecah menjadi beberapa bubble pendek.\n"
            "- Lakukan upsell hanya jika sesuai konteks dan sopan.\n"
            "- Jika konteks tidak cukup, minta klarifikasi singkat.\n"
            "- Hormati jadwal kerja jika disediakan.\n"
        )
        logger.debug("Prompt built for tenant=%s user=%s", payload.tenant_id, payload.user_id)
        return prompt
