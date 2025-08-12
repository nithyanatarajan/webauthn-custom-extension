# ext_utils.py

import time

import httpx

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from passkey_server.config import Config
from passkey_server.exceptions.errors import ExtensionValidationError


def verify_extension_with_retries(extension_path: str):
    for attempt in range(Config.EXT_MAX_RETRIES):
        try:
            response = httpx.post(
                f'{Config.EXT_SERVER_URL}/{extension_path}/verify',
                timeout=Config.EXT_SERVER_TIMEOUT,
            )

            # 🚫 Permanent failure → do not retry
            if HTTP_400_BAD_REQUEST <= response.status_code < HTTP_500_INTERNAL_SERVER_ERROR:
                raise ExtensionValidationError(f'Extension validation failed: {response.text}')

            # ✅ Raise for other HTTP issues (e.g., 5xx)
            response.raise_for_status()
            return response.json()

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Final attempt failed
            if attempt == Config.EXT_MAX_RETRIES - 1:
                raise ExtensionValidationError('Extension server unreachable') from e

            time.sleep(1.0)  # ⏳ Backoff before retry

    return None  # Not expected to reach here
