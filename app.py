"""HiveBox API for application and temperature information."""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from statistics import mean

import httpx
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

APP_VERSION = "v0.1.0"
OPENSENSEMAP_URL = "https://api.opensensemap.org"
SENSEBOX_IDS_VARIABLE = "SENSEBOX_IDS"

DEFAULT_SENSEBOX_IDS = (
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
)

MAX_MEASUREMENT_AGE = timedelta(hours=1)

app = FastAPI(
    title="HiveBox",
    version=APP_VERSION,
)

Instrumentator().instrument(app).expose(app)


def get_sensebox_ids() -> tuple[str, ...]:
    """Return senseBox IDs from the environment or use defaults."""
    configured_value = os.getenv(SENSEBOX_IDS_VARIABLE, "")

    configured_ids = tuple(
        box_id.strip()
        for box_id in configured_value.split(",")
        if box_id.strip()
    )

    return configured_ids or DEFAULT_SENSEBOX_IDS


async def fetch_box(
    client: httpx.AsyncClient,
    box_id: str,
) -> dict | None:
    """Retrieve one senseBox, returning None when unavailable."""
    try:
        response = await client.get(
            f"{OPENSENSEMAP_URL}/boxes/{box_id}"
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError):
        return None


async def fetch_boxes() -> list[dict]:
    """Retrieve all configured senseBoxes concurrently."""
    timeout = httpx.Timeout(
        connect=15.0,
        read=300.0,
        write=15.0,
        pool=15.0,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        results = await asyncio.gather(
            *(
                fetch_box(client, box_id)
                for box_id in get_sensebox_ids()
            )
        )

    return [box for box in results if box is not None]


def extract_current_temperatures(
    boxes: list[dict],
    current_time: datetime | None = None,
) -> list[float]:
    """Extract Celsius temperatures measured during the last hour."""
    now = current_time or datetime.now(timezone.utc)
    oldest_allowed = now - MAX_MEASUREMENT_AGE
    temperatures = []

    for box in boxes:
        for sensor in box.get("sensors", []):
            title = sensor.get("title", "").casefold()
            unit = sensor.get("unit", "")
            measurement = sensor.get("lastMeasurement") or {}

            is_temperature = (
                "temperature" in title
                or "temperatur" in title
            )

            if not is_temperature:
                continue

            if unit not in {"°C", "C", "Celsius"}:
                continue

            value = measurement.get("value")
            measured_at_text = measurement.get("createdAt")

            if value is None or measured_at_text is None:
                continue

            try:
                temperature = float(value)
                measured_at = datetime.fromisoformat(
                    measured_at_text.replace("Z", "+00:00")
                )
            except (TypeError, ValueError):
                continue

            if measured_at.tzinfo is None:
                measured_at = measured_at.replace(
                    tzinfo=timezone.utc
                )

            if oldest_allowed <= measured_at <= now:
                temperatures.append(temperature)

    return temperatures


def get_temperature_status(temperature: float) -> str:
    """Describe whether a temperature is suitable."""
    if temperature < 10:
        return "Too Cold"

    if temperature > 37:
        return "Too Hot"

    return "Good"


@app.get("/version")
def get_version() -> dict[str, str]:
    """Return the deployed application version."""
    return {"version": APP_VERSION}


@app.get("/temperature")
async def get_temperature() -> dict[str, float | int | str]:
    """Return the average current temperature."""
    boxes = await fetch_boxes()
    temperatures = extract_current_temperatures(boxes)

    if not temperatures:
        raise HTTPException(
            status_code=503,
            detail=(
                "No temperature measurements "
                "from the last hour"
            ),
        )

    average_temperature = round(mean(temperatures), 2)

    return {
        "average": average_temperature,
        "unit": "°C",
        "measurements": len(temperatures),
        "status": get_temperature_status(
            average_temperature
        ),
    }

