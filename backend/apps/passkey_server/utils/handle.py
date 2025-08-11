import hashlib


def get_user_handle(username: str) -> bytes:
    """
    Derive a stable 16-byte user handle from the username.
    """
    return hashlib.sha256(username.encode('utf-8')).digest()[:16]
