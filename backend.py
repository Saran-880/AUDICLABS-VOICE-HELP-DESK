
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

BASE_URL = "https://api.audiclabs.com/v1"
TIMEOUT = 15

logger = logging.getLogger(__name__)


class AudicLabsError(RuntimeError):
    """A safe, user-facing AudicLabs integration error."""


def _headers():
    """Build authentication headers without exposing the API key."""
    api_key = os.getenv("AUDICLABS_API_KEY")

    if not api_key:
        raise AudicLabsError(
            "AUDICLABS_API_KEY is missing from the server environment."
        )

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _request(method, endpoint, **kwargs):
    """Make an API request with safe error messages and request-ID logging."""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    try:
        response = requests.request(
            method,
            url,
            headers=_headers(),
            timeout=TIMEOUT,
            **kwargs,
        )

        request_id = response.headers.get("X-Request-Id")
        if request_id:
            logger.info(
                "AudicLabs API request completed: endpoint=%s request_id=%s status=%s",
                endpoint,
                request_id,
                response.status_code,
            )

        if response.status_code == 401:
            raise AudicLabsError(
                "AudicLabs rejected the API key. Check server configuration."
            )

        if response.status_code == 402:
            raise AudicLabsError(
                "AudicLabs reports insufficient credits. Check your account."
            )

        if response.status_code == 403:
            raise AudicLabsError(
                f"The API key does not have permission for {endpoint}."
            )

        if response.status_code == 413:
            raise AudicLabsError(
                "The request is too large for the AudicLabs service."
            )

        if response.status_code == 422:
            raise AudicLabsError(
                "AudicLabs rejected the request format or input."
            )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            message = "AudicLabs rate limit reached."
            if retry_after:
                message += f" Please retry after {retry_after} seconds."
            raise AudicLabsError(message)

        if response.status_code == 503:
            retry_after = response.headers.get("Retry-After")
            message = "AudicLabs service is temporarily unavailable."
            if retry_after:
                message += f" Please retry after {retry_after} seconds."
            raise AudicLabsError(message)

        response.raise_for_status()

        if not response.content:
            return {}

        try:
            return response.json()
        except ValueError as exc:
            raise AudicLabsError(
                "AudicLabs returned an unexpected response format."
            ) from exc

    except requests.Timeout as exc:
        raise AudicLabsError(
            "The AudicLabs request timed out. Please try again."
        ) from exc

    except requests.RequestException as exc:
        # Do not log request headers, credentials, or response bodies.
        logger.warning(
            "AudicLabs request failed: endpoint=%s error_type=%s",
            endpoint,
            type(exc).__name__,
        )
        raise AudicLabsError(
            "Could not connect to the AudicLabs service."
        ) from exc


def create_ticket(service: str) -> dict:
    """Create a single-use browser ticket for STT or TTS."""
    if service not in {"stt", "tts"}:
        raise ValueError("service must be 'stt' or 'tts'")

    data = _request(
        "POST",
        "/tickets",
        json={"service": service, "endpoint": "stream"},
    )

    if not data.get("ticket") or not data.get("url"):
        raise AudicLabsError(
            "The ticket response did not contain the expected ticket and URL."
        )

    return {
        "ticket": data["ticket"],
        "url": data["url"],
    }


def check_health() -> dict:
    """Check the documented Noise Suppressor health endpoint."""
    return _request("GET", "/noise-suppressor/health")


def get_stt_languages() -> dict:
    """Retrieve supported speech-to-text languages."""
    return _request("GET", "/stt/languages")


def get_stt_models() -> dict:
    """Retrieve available speech-to-text models."""
    return _request("GET", "/stt/models")


def get_tts_voices() -> dict:
    """Retrieve available text-to-speech voices."""
    return _request("GET", "/tts/voices")


def get_tts_languages() -> dict:
    """Retrieve supported text-to-speech languages."""
    return _request("GET", "/tts/languages")
