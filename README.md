# AI Agent Backend (Gemini) — Backend Skeleton + Persistence

Branch: `feature/contacts-history` (backend)

## Ringkas
Backend FastAPI untuk AI Agent dengan persistence, per-tenant auth, RAG embeddings (Gemini atau lokal), scheduler follow-up sederhana (polling), upload KB, dan kontak + log percakapan (CRM-ready).

## Arsitektur Singkat
- `app/main.py` — FastAPI app, CORS, error handlers, router registrasi, auto create table (opsional).
- `app/routers/` — endpoint: `chat`, `kb` (knowledge base), `tenants`, `followup`, `contacts`, `health`.
- `app/services/` — orchestrator, prompt builder, post-processing (split bubble), RAG dengan embeddings (DB), follow-up (DB), tenant service, embedding client (Gemini/local), follow-up scheduler (polling), ingest file, contact/log service.
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
   EMBEDDING_PROVIDER=gemini   # atau local
   EMBEDDING_MODEL_NAME=models/embedding-001   # atau sentence-transformers/all-MiniLM-L6-v2 untuk lokal
   ```

## Menjalankan
```
python main.py
# Uvicorn jalan di http://0.0.0.0:8000
```
Header wajib: `X-API-Key: <tenant_or_global_key>`.  
Untuk tenant-scope, sertakan juga `X-Tenant-Id: <tenant_id>`.

## Endpoint utama
- `POST /chat` — payload `ChatRequest` (tenant_id, user_id, messages[], channel, locale). Alur: retrieve konteks (DB RAG), build prompt (persona + SOP), panggil LLM, pecah jawaban jadi bubble.
- `POST /kb/upsert` — tambah/ubah pengetahuan (DB) + simpan embedding. Membutuhkan tenant sudah ada.
- `POST /kb/upload` — upload file (pdf/txt/md/csv/tsv/xlsx) multipart, otomatis parse→chunk→embed→KB.
- `GET /tenants/{tenant_id}/settings` — ambil konfigurasi tenant (persona, SOP, jam kerja, API key).
- `PUT /tenants/{tenant_id}/settings` — buat/perbarui tenant; jika `api_key` kosong akan dibuat random.
- `POST /followup/schedule` — jadwalkan follow-up (DB).
- `GET /followup/pending` — lihat antrian follow-up per tenant (pending).
- `GET /followup?status=pending|sent|failed` — filter follow-up per status.
- `POST /contacts` — create/update contact (nama/phone/email, per tenant).
- `GET /contacts` — list contacts per tenant.
- `GET /contacts/{id}` — detail contact.
- `POST /contacts/logs` — simpan log percakapan (history).
- `GET /contacts/logs` — list history (opsional filter contact_id).
- `GET /health` — status sederhana.

## Batasan saat ini
- Follow-up dispatch masih polling di dalam app (belum ada queue/worker dan belum kirim ke channel).
- Upload KB: belum ada antrian/worker; parsing synchronous; mendukung pdf/txt/md/csv/tsv/xlsx sederhana.
- Belum ada channel adapter (WA/Telegram), belum ada media/STT/TTS.
- Belum ada rate limiting dan telemetry/metrics.
- Kontak/log belum terhubung ke CRM eksternal; belum ada webhook/connector.

## Rekomendasi next steps
1) Integrasi queue/worker (Redis) untuk follow-up/reminder dispatch dan pengiriman ke channel.  
2) Integrasi vector DB/ANN (Weaviate/PGVector/Redis) untuk skala besar.  
3) Hardening auth: key per-tenant rotasi, rate limiting, logging terstruktur + metrics.  
4) Channel adapter pertama (Telegram/WA) + media handling + shipping API nyata.  
5) CRM hook: webhook/connector untuk sync contact/deal, plus contact dedup lebih kuat.  

## Embeddings
- Provider configurable: `gemini` (default) atau `local`.
- Env:
  - `EMBEDDING_PROVIDER=gemini|local`
  - `EMBEDDING_MODEL_NAME`:
    - Gemini: `models/embedding-001`
    - Local example: `sentence-transformers/all-MiniLM-L6-v2`
- Jika `gemini` rate-limit, switch ke `local` (butuh `sentence-transformers` + model download).
