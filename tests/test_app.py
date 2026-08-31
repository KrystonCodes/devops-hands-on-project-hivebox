"""Unit tests for the HiveBox API."""

from datetime import datetime, timedelta, timezone

import pytest
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
    assert response.json() == {"version": "v0.1.0"}


def test_default_sensebox_ids(
    monkeypatch,
) -> None:
    """Default IDs are used when the environment is unset."""
    monkeypatch.delenv(
        hivebox.SENSEBOX_IDS_VARIABLE,
        raising=False,
    )

    assert (
        hivebox.get_sensebox_ids()
        == hivebox.DEFAULT_SENSEBOX_IDS
    )


def test_configured_sensebox_ids(
    monkeypatch,
) -> None:
    """IDs can be supplied as a comma-separated value."""
    monkeypatch.setenv(
        hivebox.SENSEBOX_IDS_VARIABLE,
        "box-one, box-two,",
    )

    assert hivebox.get_sensebox_ids() == (
        "box-one",
        "box-two",
    )


@pytest.mark.parametrize(
    ("temperature", "expected_status"),
    [
        (9.99, "Too Cold"),
        (10.0, "Good"),
        (37.0, "Good"),
        (37.01, "Too Hot"),
    ],
)
def test_temperature_status(
    temperature: float,
    expected_status: str,
) -> None:
    """Temperatures receive the expected status."""
    assert (
        hivebox.get_temperature_status(temperature)
        == expected_status
    )


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
        "status": "Good",
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


def test_metrics_endpoint() -> None:
    """Prometheus metrics are exposed by the application."""
    client.get("/version")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
