from datetime import UTC, datetime

import jwt

from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError

from passkey_server.config import Config


def encode_challenge_token(payload: dict) -> str:
    issued_at = int(datetime.now(UTC).timestamp())
    payload = {
        **payload,
        'aud': Config.JWT_AUDIENCE,  # Audience for the token
        'iss': Config.JWT_ISSUER,  # 'iss': trusted issuing domain
        'iat': issued_at,  # Issued at (Unix timestamp)
        'exp': issued_at + Config.JWT_EXPIRY_SECONDS,  # Expiration (60s from iat)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)


def decode_challenge_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            options={'require': ['exp', 'iat', 'iss']},
            leeway=Config.JWT_LEEWAY_SECONDS,
            issuer=Config.JWT_ISSUER,
            audience=Config.JWT_AUDIENCE,
        )

        return payload

    except ExpiredSignatureError as e:
        raise ExpiredSignatureError(f'Token expired: {e!s}') from e

    except PyJWTError as e:
        # Catch all PyJWT errors here
        raise InvalidTokenError(f'Token validation error: {e!s}') from e
