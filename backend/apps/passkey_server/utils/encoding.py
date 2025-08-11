import base64


def b64url_decode(data: str) -> bytes:
    """Base64URL decode with correct padding"""
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)
