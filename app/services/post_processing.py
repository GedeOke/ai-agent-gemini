from textwrap import wrap
from typing import List

from app.models.schemas import Bubble


class PostProcessor:
    def __init__(self, max_bubble_length: int = 280) -> None:
        self.max_bubble_length = max_bubble_length

    def split_bubbles(self, text: str) -> List[Bubble]:
        chunks = wrap(text, self.max_bubble_length, break_long_words=False, replace_whitespace=False)
        return [Bubble(text=chunk.strip(), delay_ms=1200 if idx else 0) for idx, chunk in enumerate(chunks)]
