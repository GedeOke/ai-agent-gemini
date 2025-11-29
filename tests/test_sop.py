import os
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

# Make project importable when running as script
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Configure env BEFORE importing app
os.environ["API_KEY"] = ""
db_path = ROOT / "test_sop.db"
if db_path.exists():
    db_path.unlink()
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
os.environ.setdefault("AUTO_CREATE_TABLES", "true")
os.environ.setdefault("EMBEDDING_PROVIDER", "local")
os.environ.setdefault("GEMINI_API_KEY", "")

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _create_tenant(client):
    payload = {
        "tenant_id": "demo",
        "persona": {"persona": "sales", "style_prompt": "Ramah dan ringkas", "tone": "neutral", "language": "id"},
        "sop": {
            "steps": [
                {"name": "reach out", "description": "Reach out", "order": 1},
                {"name": "keluhan", "description": "Keluhan", "order": 2},
                {"name": "konsultasi", "description": "Konsultasi", "order": 3},
                {"name": "rekomendasi", "description": "Rekomendasi", "order": 4},
                {"name": "harga", "description": "Harga", "order": 5},
            ]
        },
        "working_hours": "09:00-17:00",
        "timezone": "Asia/Jakarta",
        "followup_enabled": True,
        "followup_interval_minutes": 60,
    }
    res = client.put("/tenants/demo/settings", json=payload, headers={"X-API-Key": os.environ.get("API_KEY", "")})
    assert res.status_code == 200, res.text
    data = res.json()
    return data["api_key"]


def test_sop_state_flow(client):
    tenant_api_key = _create_tenant(client)
    headers = {"X-API-Key": tenant_api_key, "X-Tenant-Id": "demo"}

    # create contact
    res = client.post(
        "/contacts",
        json={"tenant_id": "demo", "name": "Budi", "phone": "+628123456789"},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    contact_id = res.json()["id"]

    # set state manual
    res = client.put(
        "/sop/state",
        json={"tenant_id": "demo", "contact_id": contact_id, "user_id": "u1", "current_step": "keluhan"},
        headers=headers,
    )
    assert res.status_code == 200, res.text

    # get state
    res = client.get(f"/sop/state?contact_id={contact_id}&user_id=u1", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["current_step"] == "keluhan"

    # move to next step
    res = client.put(
        "/sop/state",
        json={"tenant_id": "demo", "contact_id": contact_id, "user_id": "u1", "current_step": "harga"},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    res = client.get(f"/sop/state?contact_id={contact_id}&user_id=u1", headers=headers)
    assert res.status_code == 200
    assert res.json()["current_step"] == "harga"


def test_contact_logs(client):
    tenant_api_key = _create_tenant(client)
    headers = {"X-API-Key": tenant_api_key, "X-Tenant-Id": "demo"}
    res = client.post(
        "/contacts",
        json={"tenant_id": "demo", "name": "Ana", "phone": "+628111111"},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    contact_id = res.json()["id"]

    # log message
    res = client.post(
        "/contacts/logs",
        json={
            "tenant_id": "demo",
            "contact_id": contact_id,
            "user_id": "u2",
            "role": "user",
            "content": "Halo",
            "metadata": {"channel": "web"},
        },
        headers=headers,
    )
    assert res.status_code == 200, res.text

    # get logs
    res = client.get(f"/contacts/logs?contact_id={contact_id}", headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert isinstance(data, list)
    assert any(msg["content"] == "Halo" for msg in data)
