"""Unit tests for the HiveBox API."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

import app as hivebox

client = TestClient(hivebox.app)


def make_temperature(
    value: str,
    measured_at: datetime,
) -> dict:
    """Create an openSenseMap-like temperature sensor."""
    return {
        "title": "Temperatur",
        "unit": "°C",
        "lastMeasurement": {
            "value": value,
            "createdAt": measured_at.isoformat(),
        },
    }


def test_version_endpoint() -> None:
    """The version endpoint returns the application version."""
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "v0.0.1"}


def test_temperature_endpoint_averages_fresh_data(
    monkeypatch,
) -> None:
    """Fresh values are averaged while stale values are ignored."""
    now = datetime.now(timezone.utc)

    fake_boxes = [
        {
            "sensors": [
                make_temperature(
                    "20",
                    now - timedelta(minutes=10),
                ),
                make_temperature(
                    "100",
                    now - timedelta(hours=2),
                ),
            ]
        },
        {
            "sensors": [
                make_temperature(
                    "24",
                    now - timedelta(minutes=20),
                )
            ]
        },
    ]

    async def fake_fetch_boxes() -> list[dict]:
        return fake_boxes

    monkeypatch.setattr(
        hivebox,
        "fetch_boxes",
        fake_fetch_boxes,
    )

    response = client.get("/temperature")

    assert response.status_code == 200
    assert response.json() == {
        "average": 22.0,
        "unit": "°C",
        "measurements": 2,
    }


def test_temperature_endpoint_rejects_stale_data(
    monkeypatch,
) -> None:
    """A 503 response is returned when every value is stale."""
    old_time = datetime.now(timezone.utc) - timedelta(hours=2)

    fake_boxes = [
        {
            "sensors": [
                make_temperature("20", old_time),
            ]
        }
    ]

    async def fake_fetch_boxes() -> list[dict]:
        return fake_boxes

    monkeypatch.setattr(
        hivebox,
        "fetch_boxes",
        fake_fetch_boxes,
    )

    response = client.get("/temperature")

    assert response.status_code == 503
    assert response.json() == {
        "detail": (
            "No temperature measurements "
            "from the last hour"
        )
    }


def test_temperature_endpoint_handles_no_boxes(
    monkeypatch,
) -> None:
    """A 503 response is returned when no boxes are available."""

    async def fake_fetch_boxes() -> list[dict]:
        return []

    monkeypatch.setattr(
        hivebox,
        "fetch_boxes",
        fake_fetch_boxes,
    )

    response = client.get("/temperature")

    assert response.status_code == 503
