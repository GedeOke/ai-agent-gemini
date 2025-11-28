# AI Agent Backend (Gemini) — Backend Skeleton + Persistence

Branch: `feature/persistence-and-auth`

## Ringkas
Backend FastAPI untuk AI Agent dengan kerangka dasar dan persistence awal: chat orchestrator, prompt builder, bubble splitter, RAG stub DB-backed, follow-up stub DB-backed, dan guard API key per-tenant atau global. Cocok jadi pondasi sebelum tambah vector store, channel messaging, dan scheduler/worker.

## Arsitektur Singkat
- `app/main.py` — FastAPI app, CORS, error handlers, router registrasi, auto create table (opsional).
- `app/routers/` — endpoint: `chat`, `kb` (knowledge base), `tenants`, `followup`, `health`.
- `app/services/` — orchestrator, prompt builder, post-processing (split bubble), RAG stub (DB), follow-up (DB), tenant service.
- `app/adapters/` — Gemini client, shipping mock.
- `app/utils/` — logging setup, API key gate (per-tenant / global).
- `app/models/` — `db_models.py` (SQLAlchemy ORM) dan `schemas.py` (Pydantic).
- `app/db.py` — async engine + session maker (SQLAlchemy).
- `app/dependencies.py` — singletons (stateless services) dan helper session.

## Persiapan
1) Python 3.11+ (disarankan venv):  
   `python -m venv venv && venv/Scripts/activate` (Windows)
2) Install deps:  
   `pip install -r requirements.txt`
3) Siapkan `.env` minimal:
   ```
   API_KEY=changeme_global   # opsional; fallback jika tidak pakai tenant key
   GEMINI_API_KEY=your_gemini_key
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname   # atau sqlite+aiosqlite:///./local.db untuk lokal
   CORS_ORIGINS=*
   AUTO_CREATE_TABLES=true
   ```

## Menjalankan
```
python main.py
# Uvicorn jalan di http://0.0.0.0:8000
```
Header wajib: `X-API-Key: <tenant_or_global_key>`.  
Untuk tenant-scope, sertakan juga `X-Tenant-Id: <tenant_id>`.

## Endpoint utama
- `POST /chat` — payload `ChatRequest` (tenant_id, user_id, messages[], channel, locale). Alur: retrieve konteks (keyword, DB), build prompt (persona + SOP), panggil Gemini, pecah jawaban jadi bubble.
- `POST /kb/upsert` — tambah/ubah pengetahuan (DB). Membutuhkan tenant sudah ada.
- `GET /tenants/{tenant_id}/settings` — ambil konfigurasi tenant (persona, SOP, jam kerja, API key).
- `PUT /tenants/{tenant_id}/settings` — buat/perbarui tenant; jika `api_key` kosong akan dibuat random.
- `POST /followup/schedule` — jadwalkan follow-up (DB).
- `GET /followup/pending` — lihat antrian follow-up per tenant.
- `GET /health` — status sederhana.

## Batasan saat ini
- RAG masih keyword match; belum vector store/embeddings.
- Follow-up masih sekadar simpan DB; belum ada scheduler/worker.
- Belum ada channel adapter (WA/Telegram), belum ada media/STT/TTS.
- Belum ada rate limiting dan telemetry/metrics.

## Rekomendasi next steps
1) Tambah vector store + embeddings (Gemini/open-source) untuk RAG; simpan embedding di DB/Redis.  
2) Tambah scheduler/worker (Redis/Queue) untuk follow-up & reminder.  
3) Hardening auth: key per-tenant rotasi, rate limiting, logging terstruktur + metrics.  
4) Channel adapter pertama (Telegram/WA) + media handling + shipping API nyata.
