# AI Agent Backend (Gemini) — Backend Skeleton

Branch: `feature/backend-skeleton`

## Ringkas
Backend FastAPI untuk AI Agent dengan kerangka dasar: chat orchestrator, prompt builder, bubble splitter, RAG stub, follow-up stub, dan guard API key. Cocok jadi pondasi sebelum tambah DB, vector store, dan channel messaging.

## Arsitektur Singkat
- `app/main.py` — FastAPI app, CORS, error handlers, router registrasi.
- `app/routers/` — endpoint: `chat`, `kb` (knowledge base), `tenants`, `followup`, `health`.
- `app/services/` — orchestrator, prompt builder, post-processing (split bubble), RAG stub, follow-up stub.
- `app/adapters/` — Gemini client, shipping mock.
- `app/utils/` — logging setup, API key gate.
- `app/dependencies.py` — singletons sementara (RAG, followup, orchestrator, tenant settings in-memory).
- `app/models/schemas.py` — Pydantic schemas untuk request/response.

## Persiapan
1) Python 3.11+ (disarankan venv):  
   `python -m venv venv && venv/Scripts/activate` (Windows)
2) Install deps:  
   `pip install -r requirements.txt`
3) Siapkan `.env` minimal:
   ```
   API_KEY=changeme
   GEMINI_API_KEY=your_gemini_key
   CORS_ORIGINS=*
   ```

## Menjalankan
```
python main.py
# Uvicorn jalan di http://0.0.0.0:8000
```
Header wajib untuk semua endpoint: `X-API-Key: <API_KEY>`

## Endpoint utama
- `POST /chat` — payload `ChatRequest` (tenant_id, user_id, messages[], channel, locale). Alur: retrieve konteks (stub), build prompt (persona + SOP), panggil Gemini, pecah jawaban jadi bubble.
- `POST /kb/upsert` — tambah pengetahuan (masih in-memory).
- `GET /tenants/{tenant_id}/settings` — ambil konfigurasi tenant (persona, SOP, jam kerja).
- `PUT /tenants/{tenant_id}/settings` — perbarui konfigurasi tenant.
- `POST /followup/schedule` — jadwalkan follow-up (stub queue).
- `GET /followup/pending` — lihat antrian follow-up.
- `GET /health` — status sederhana.

## Batasan saat ini
- Data masih in-memory (hilang saat restart), belum ada Postgres/Redis.
- RAG sekadar keyword match; belum vector store/embeddings.
- Follow-up & shipping masih mock/stub.
- Belum ada channel adapter (WA/Telegram), belum ada media/STT/TTS.

## Rekomendasi next steps
1) Tambah DB (Postgres) + Redis untuk queue; ganti store in-memory.  
2) Implement vector store + embeddings (Gemini/open-source) untuk RAG dan SOP state machine.  
3) Auth per-tenant yang lebih kuat (JWT/key per-tenant) + rate limiting & observability.  
4) Channel adapter pertama (Telegram/WA) + media handling + shipping API nyata.
