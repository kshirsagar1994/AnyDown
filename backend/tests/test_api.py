import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["ffmpeg"] == "available"

def test_platforms_endpoint():
    res = client.get("/api/v1/platforms")
    assert res.status_code == 200
    data = res.json()
    assert "platforms" in data
    assert len(data["platforms"]) > 0
    assert "legal_disclaimer" in data

def test_analyze_invalid_url():
    res = client.post("/api/v1/analyze", json={"url": "not-a-valid-url"})
    assert res.status_code == 400
    data = res.json()
    assert "error" in data

def test_analyze_unsupported_platform():
    res = client.post("/api/v1/analyze", json={"url": "https://random-unknown-site.org/video"})
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] in ("UNSUPPORTED_PLATFORM", "INVALID_URL")

def test_analyze_and_download_flow_mock():
    # 1. Analyze mock fixture
    res = client.post("/api/v1/analyze", json={"url": "https://mock-media.anydown.local/test-video"})
    assert res.status_code == 200
    data = res.json()
    analysis_id = data["analysis_id"]
    formats = data["formats"]
    assert len(formats) > 0

    chosen_format = formats[0]["format_id"]

    # 2. Start download job
    res = client.post("/api/v1/downloads", json={
        "analysis_id": analysis_id,
        "format_id": chosen_format
    })
    assert res.status_code == 200
    job_data = res.json()
    job_id = job_data["job_id"]
    assert job_data["status"] in ("queued", "downloading", "converting", "completed")

    # 3. Check job status
    res = client.get(f"/api/v1/downloads/{job_id}")
    assert res.status_code == 200
    status_data = res.json()
    assert status_data["job_id"] == job_id

def test_download_invalid_format():
    # Analyze mock fixture
    res = client.post("/api/v1/analyze", json={"url": "https://mock-media.anydown.local/test-video"})
    analysis_id = res.json()["analysis_id"]

    # Try downloading non-existent format
    res = client.post("/api/v1/downloads", json={
        "analysis_id": analysis_id,
        "format_id": "non-existent-8k-format"
    })
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "FORMAT_UNAVAILABLE"

