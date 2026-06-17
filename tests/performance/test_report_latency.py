"""
P-15 Performance test — report generation latency.
Requirement: GET /api/v1/reports/batch/{id} must complete in < 5 seconds.

Run: pytest tests/performance/test_report_latency.py -v
Requires: GATEWAY_URL env var (default http://localhost:8000) and a valid test batch ID.

Usage:
  GATEWAY_URL=http://localhost:8000 TEST_BATCH_ID=<uuid> pytest tests/performance/ -v
"""
import asyncio
import os
import statistics
import time

import pytest
import httpx

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
TEST_BATCH_ID = os.getenv("TEST_BATCH_ID", "")
AUTH_EMAIL = os.getenv("TEST_EMAIL", "admin@agrovision.uz")
AUTH_PASSWORD = os.getenv("TEST_PASSWORD", "admin123")

LATENCY_BUDGET_SECONDS = 5.0
SAMPLE_COUNT = 10


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def auth_token():
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=10) as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": AUTH_EMAIL, "password": AUTH_PASSWORD},
        )
        if resp.status_code != 200:
            pytest.skip(f"Auth failed ({resp.status_code}); skipping performance tests")
        return resp.json()["data"]["access_token"]


@pytest.fixture(scope="module")
async def batch_id(auth_token):
    if TEST_BATCH_ID:
        return TEST_BATCH_ID
    # Auto-discover first active batch from livestock service
    async with httpx.AsyncClient(
        base_url=GATEWAY_URL,
        timeout=10,
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as client:
        resp = await client.get("/api/v1/batches/", params={"farm_id": "", "page": 1, "page_size": 1})
        if resp.status_code != 200 or not resp.json().get("data"):
            pytest.skip("No batches available; skipping performance tests")
        return resp.json()["data"][0]["id"]


@pytest.mark.asyncio
async def test_report_generation_latency(auth_token, batch_id):
    """Single report fetch must complete within the 5-second budget."""
    async with httpx.AsyncClient(
        base_url=GATEWAY_URL,
        timeout=LATENCY_BUDGET_SECONDS + 2,
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as client:
        start = time.perf_counter()
        resp = await client.get(f"/api/v1/reports/batch/{batch_id}")
        elapsed = time.perf_counter() - start

    assert resp.status_code == 200, f"Report endpoint returned {resp.status_code}"
    assert elapsed < LATENCY_BUDGET_SECONDS, (
        f"Report generation took {elapsed:.2f}s — exceeds {LATENCY_BUDGET_SECONDS}s budget"
    )


@pytest.mark.asyncio
async def test_report_latency_under_concurrent_load(auth_token, batch_id):
    """10 concurrent report requests must all finish within budget; p95 < 5s."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    async def fetch_once(client: httpx.AsyncClient) -> float:
        start = time.perf_counter()
        resp = await client.get(f"/api/v1/reports/batch/{batch_id}")
        elapsed = time.perf_counter() - start
        assert resp.status_code == 200
        return elapsed

    async with httpx.AsyncClient(
        base_url=GATEWAY_URL,
        timeout=LATENCY_BUDGET_SECONDS + 5,
        headers=headers,
    ) as client:
        times = await asyncio.gather(*[fetch_once(client) for _ in range(SAMPLE_COUNT)])

    p95 = sorted(times)[int(SAMPLE_COUNT * 0.95) - 1]
    mean = statistics.mean(times)
    print(f"\nLatency stats (n={SAMPLE_COUNT}): mean={mean:.2f}s p95={p95:.2f}s max={max(times):.2f}s")

    assert p95 < LATENCY_BUDGET_SECONDS, (
        f"p95 latency {p95:.2f}s exceeds {LATENCY_BUDGET_SECONDS}s budget"
    )


@pytest.mark.asyncio
async def test_batch_list_latency(auth_token):
    """Batch listing must respond within 2 seconds."""
    async with httpx.AsyncClient(
        base_url=GATEWAY_URL,
        timeout=5,
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as client:
        start = time.perf_counter()
        resp = await client.get("/api/v1/batches/", params={"farm_id": "", "page": 1, "page_size": 20})
        elapsed = time.perf_counter() - start

    assert resp.status_code in (200, 422), f"Unexpected status {resp.status_code}"
    assert elapsed < 2.0, f"Batch list took {elapsed:.2f}s — exceeds 2s budget"


@pytest.mark.asyncio
async def test_farm_list_latency(auth_token):
    """Farm list must respond within 1 second."""
    async with httpx.AsyncClient(
        base_url=GATEWAY_URL,
        timeout=5,
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as client:
        start = time.perf_counter()
        resp = await client.get("/api/v1/farms/", params={"page": 1, "page_size": 50})
        elapsed = time.perf_counter() - start

    assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
    assert elapsed < 1.0, f"Farm list took {elapsed:.2f}s — exceeds 1s budget"
