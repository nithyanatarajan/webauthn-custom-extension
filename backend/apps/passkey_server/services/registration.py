import base64
import logging

from fido2.webauthn import PublicKeyCredentialUserEntity

from passkey_server.config import Config
from passkey_server.utils.handle import get_user_handle
from passkey_server.utils.jwt import decode_challenge_token, encode_challenge_token

from .extensions import get_available_extensions, get_extensions_from, validate_extensions
from .rp_server import server
from .store import store_credential

logger = logging.getLogger(__name__)


# ---- Registration ----
def start(username: str) -> tuple[dict, str]:
    """
    Begins the WebAuthn registration ceremony for a given username.

    Returns:
        - publicKeyCredentialCreationOptions (dict)
        - challenge_token (JWT-encoded state)
    """
    # 1. Generate user handle (should be stable across logins)
    user_handle = get_user_handle(username)

    # 2. Create user entity
    user = PublicKeyCredentialUserEntity(id=user_handle, name=username, display_name=username)

    # 3. Begin registration ceremony
    options, state = server.register_begin(
        user=user,
        credentials=[],
        resident_key_requirement='preferred',
        user_verification='discouraged',
        authenticator_attachment='cross-platform',
        extensions=get_available_extensions(),
    )

    # 4. Embed state metadata into token (for stateless verification)
    state['username'] = username
    state['user_handle'] = base64.urlsafe_b64encode(user_handle).decode('utf-8')

    # 5. Return as tuple (options, challenge_token)
    return dict(options), encode_challenge_token(state)


def finish(attestation: dict, challenge_token: str) -> bool:
    """
    Completes the WebAuthn registration process.

    Validates the signed challenge, attestation response, and account-level token.
    Saves credential to in-memory store on success.
    """

    # 1. Decode and validate challenge token (issued during /register/begin)
    state = decode_challenge_token(challenge_token)
    username = state.get('username')
    user_handle_b64 = state.get('user_handle')
    if not (username and user_handle_b64):
        raise ValueError('Malformed challenge token')

    extensions = attestation.get('extensions', {})
    if not extensions:
        logger.warning('No extensions provided in attestation response')
    else:
        results = get_extensions_from(extensions)
        for name, data in results:
            logger.info('%s: %s', name, data)
        validate_extensions(extensions)

    # 2. Complete FIDO2/WebAuthn registration
    auth_data = server.register_complete(state, attestation)

    # 3. Decode user handle from base64
    try:
        user_handle = base64.urlsafe_b64decode(user_handle_b64.encode('utf-8'))
    except Exception as e:
        raise ValueError('Invalid user handle encoding') from e

    # 6. Store credential in in-memory DB
    store_credential(
        credential_id=auth_data.credential_data.credential_id,
        user_handle=user_handle,
        public_key=auth_data.credential_data.public_key,
        sign_count=0,
        username=username,
        rp_id=Config.RP_ID,
        credential_data=auth_data.credential_data,
    )

    logger.info('REGISTRATION SUCCESS for %s', username)
    return True
