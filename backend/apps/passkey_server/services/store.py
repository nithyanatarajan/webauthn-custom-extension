from typing import Any

# Global in-memory credential store
CREDENTIAL_STORE: dict[bytes, dict[str, Any]] = {}


def store_credential(  # noqa: PLR0913
    credential_id: bytes,
    user_handle: bytes,
    public_key: Any,
    sign_count: int,
    username: str,
    rp_id: str,
    credential_data: Any,
) -> None:
    CREDENTIAL_STORE[credential_id] = {
        'credential_id': credential_id,
        'user_handle': user_handle,
        'public_key': public_key,
        'sign_count': sign_count,
        'username': username,
        'rp_id': rp_id,
        'credential_data': credential_data,
    }


def get_credential(credential_id: bytes) -> dict[str, Any] | None:
    return CREDENTIAL_STORE.get(credential_id)


def get_credentials_for_user(user_handle: bytes) -> list[dict[str, Any]]:
    return [cred for cred in CREDENTIAL_STORE.values() if cred['user_handle'] == user_handle]


def get_credentials_for_username(username: str) -> list[dict[str, Any]]:
    return [cred for cred in CREDENTIAL_STORE.values() if cred['username'] == username]


def update_sign_count(credential_id: bytes, new_sign_count: int) -> None:
    if credential_id in CREDENTIAL_STORE:
        CREDENTIAL_STORE[credential_id]['sign_count'] = new_sign_count
