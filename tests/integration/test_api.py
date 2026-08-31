"""Integration tests for a running HiveBox server."""

import os

import httpx
import pytest


def get_base_url() -> str:
    """Return the server URL or skip the integration tests."""
    base_url = os.getenv("HIVEBOX_BASE_URL")

    if base_url is None:
        pytest.skip(
            "HIVEBOX_BASE_URL is not configured"
        )

    return base_url.rstrip("/")


@pytest.mark.integration
def test_running_version_endpoint() -> None:
    """The running application reports version v0.1.0."""
    response = httpx.get(
        f"{get_base_url()}/version",
        timeout=10.0,
    )

    response.raise_for_status()

    assert response.json() == {
        "version": "v0.1.0",
    }


@pytest.mark.integration
def test_running_metrics_endpoint() -> None:
    """The running application exposes Prometheus metrics."""
    response = httpx.get(
        f"{get_base_url()}/metrics",
        timeout=10.0,
    )

    response.raise_for_status()

    assert "http_requests_total" in response.text
