import base64
import logging

from fido2.webauthn import PublicKeyCredentialUserEntity

from passkey_server.config import Config
from passkey_server.utils.handle import get_user_handle
from passkey_server.utils.jwt import decode_challenge_token, encode_challenge_token

from .extensions import read_extensions_from, validate_extensions_for
from .extensions_registry import REGISTRATION_FLOW, get_available_extensions
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
    logger.info('REGISTRATION START for %s', username)

    # 1. Generate user handle (should be stable across logins)
    user_handle = get_user_handle(username)
    logger.debug('Generated user_handle length=%d for username=%s', len(user_handle or b''), username)

    # 2. Create user entity
    user = PublicKeyCredentialUserEntity(id=user_handle, name=username, display_name=username)

    # 3. Begin registration ceremony
    logger.debug('Calling server.register_begin with extensions')
    options, state = server.register_begin(
        user=user,
        credentials=[],
        resident_key_requirement='preferred',
        user_verification='discouraged',
        authenticator_attachment='cross-platform',
        extensions=get_available_extensions(REGISTRATION_FLOW),
    )
    logger.debug('register_begin succeeded for username=%s', username)

    # 4. Embed state metadata into token (for stateless verification)
    state['username'] = username
    state['user_handle'] = base64.urlsafe_b64encode(user_handle).decode('utf-8')

    # 5. Return as tuple (options, challenge_token)
    return dict(options), encode_challenge_token(state)


def finish(attestation: dict, challenge_token: str) -> bool:
    """
    Completes the WebAuthn registration process.

    :param attestation: WebAuthn attestation response from the browser
    :param challenge_token: JWT-encoded state from the start phase
    :return: True if registration succeeded, raises ValueError on failure
    """

    logger.debug('REGISTRATION FINISH invoked')

    # 1. Decode and validate challenge token (issued during /register/begin)
    state = decode_challenge_token(challenge_token)
    username = state.get('username')
    user_handle_b64 = state.get('user_handle')
    if not (username and user_handle_b64):
        logger.error('Malformed challenge token: username or user_handle missing')
        raise ValueError('Malformed challenge token')

    logger.info('Decoding challenge token succeeded for username=%s', username)

    # 2. Validate attestation extensions
    extensions = attestation.get('extensions', {})
    if not extensions:
        logger.warning('No extensions provided in attestation response')
    else:
        results = read_extensions_from(extensions)
        for name, data in results:
            logger.info('%s: %s', name, data)
        validate_extensions_for(extensions, REGISTRATION_FLOW)

    # 3. Complete registration ceremony
    logger.debug('Calling server.register_complete for user=%s', username)
    auth_data = server.register_complete(
        state,  # from JWT
        attestation,  # raw browser response (WebAuthn attestation)
    )
    logger.debug('register_complete succeeded for user=%s', username)

    # 4. Decode user handle from base64
    try:
        user_handle = base64.urlsafe_b64decode(user_handle_b64.encode('utf-8'))
    except Exception as e:
        logger.error('Invalid user handle encoding for user=%s', username)
        raise ValueError('Invalid user handle encoding') from e

    # 5. Store credential in in-memory DB
    store_credential(
        credential_id=auth_data.credential_data.credential_id,
        user_handle=user_handle,
        public_key=auth_data.credential_data.public_key,
        sign_count=0,
        username=username,
        rp_id=Config.RP_ID,
        credential_data=auth_data.credential_data,
    )
    logger.info('Stored credential for user=%s (rp_id=%s)', username, Config.RP_ID)

    logger.info('REGISTRATION SUCCESS for %s', username)
    return True
