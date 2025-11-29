import csv
import io
import logging
from typing import List

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
from starlette import status

from app.models.schemas import KnowledgeItem

logger = logging.getLogger(__name__)


class IngestService:
    """
    Parse uploaded files into KB chunks to be embedded and stored.
    Supported: pdf, txt, md, csv, tsv.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.allowed_types = {
            "application/pdf",
            "text/plain",
            "text/markdown",
            "text/csv",
            "text/tab-separated-values",
            "application/vnd.ms-excel",
        }

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        if not words:
            return []
        chunks = []
        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
        return chunks

    def _parse_pdf(self, data: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(data))
            texts = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    texts.append(text.strip())
            return "\n\n".join(texts)
        except Exception as exc:
            logger.exception("Failed to parse PDF")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse PDF",
            ) from exc

    def _parse_text(self, data: bytes) -> str:
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to decode text"
            ) from exc

    def _parse_csv(self, data: bytes, delimiter: str = ",") -> str:
        try:
            stream = io.StringIO(data.decode("utf-8", errors="ignore"))
            reader = csv.reader(stream, delimiter=delimiter)
            rows = [" | ".join(row) for row in reader]
            return "\n".join(rows)
        except Exception as exc:
            logger.exception("Failed to parse CSV/TSV")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse CSV/TSV",
            ) from exc

    async def parse_file(self, file: UploadFile, tags: List[str]) -> List[KnowledgeItem]:
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}",
            )
        data = await file.read()
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

        text = ""
        if file.content_type == "application/pdf":
            text = self._parse_pdf(data)
        elif file.content_type in {"text/plain", "text/markdown"}:
            text = self._parse_text(data)
        elif file.content_type in {"text/csv", "application/vnd.ms-excel"}:
            text = self._parse_csv(data, delimiter=",")
        elif file.content_type == "text/tab-separated-values":
            text = self._parse_csv(data, delimiter="\t")

        text = text.strip()
        if not text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No text extracted from file")

        chunks = self._chunk_text(text)
        items: List[KnowledgeItem] = []
        for idx, chunk in enumerate(chunks, start=1):
            items.append(
                KnowledgeItem(
                    title=f"{file.filename or 'document'} - part {idx}",
                    content=chunk,
                    tags=tags,
                )
            )
        return items
