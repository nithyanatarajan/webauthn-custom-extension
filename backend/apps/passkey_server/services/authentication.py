import logging

from fido2.webauthn import PublicKeyCredentialDescriptor, PublicKeyCredentialType

from passkey_server.utils.encoding import b64url_decode
from passkey_server.utils.jwt import decode_challenge_token, encode_challenge_token

from .extensions import read_extensions_from, validate_extensions_for
from .extensions_registry import AUTHENTICATION_FLOW, get_available_extensions
from .rp_server import server
from .store import get_credential, get_credentials_for_username, update_sign_count

logger = logging.getLogger(__name__)


# ---- Authentication ----
def start(username: str) -> tuple[dict, str]:
    """
    Begins the WebAuthn authentication ceremony for a given username.
    :param username:
    :return:
        - publicKeyCredentialRequestOptions (dict)
        - challenge_token (JWT-encoded state)
    """
    logger.info('AUTHENTICATION START for %s', username)

    # 1. Load registered credentials for this user
    credentials = get_credentials_for_username(username)
    if not credentials:
        logger.error('No credentials found for username=%s', username)
        raise ValueError('User not found or no credentials registered')
    logger.debug('Found %d credential(s) for username=%s', len(credentials), username)

    # 2. Prepare allowCredentials list
    allow_credentials = [
        PublicKeyCredentialDescriptor(id=cred['credential_id'], type=PublicKeyCredentialType.PUBLIC_KEY)
        for cred in credentials
    ]
    logger.debug('Prepared %d allowCredential descriptor(s)', len(allow_credentials))

    # 3. Begin authentication ceremony
    logger.debug('Calling server.authenticate_begin')
    options, state = server.authenticate_begin(
        credentials=allow_credentials,
        extensions=get_available_extensions(AUTHENTICATION_FLOW),
    )
    logger.debug('authenticate_begin succeeded for username=%s', username)

    # 4. Embed state metadata into token (for stateless verification)
    state['username'] = username  # Required later during verification

    # 5. Return publicKey options + JWT-encoded state
    return dict(options), encode_challenge_token(state)


def finish(assertion: dict, challenge_token: str) -> bool:
    """
    Completes the WebAuthn authentication ceremony.

    :param assertion: WebAuthn assertion from the browser
    :param challenge_token: Encoded JWT state from /authenticate/begin
    :return: True if authentication succeeded, raises ValueError on failure
    """
    logger.debug('AUTHENTICATION FINISH invoked')

    # 1. Decode challenge token and extract session state
    state = decode_challenge_token(challenge_token)
    username = state['username']
    if not username:
        logger.error('Malformed challenge token: username missing')
        raise ValueError('Malformed challenge token')

    logger.info('Decoding challenge token succeeded for username=%s', username)

    # 2.1 Lookup credential in server-side store
    credential_id = b64url_decode(assertion['rawId'])
    stored = get_credential(credential_id)
    if not stored:
        logger.error('Credential not found for provided credential_id (user=%s)', username)
        raise ValueError('Credential not found for ID')
    logger.debug('Credential lookup succeeded for user=%s', username)

    # 2.2 Validate extensions in the assertion
    extensions = assertion.get('response', {}).get('clientExtensionResults', {})
    if not extensions:
        logger.warning('No extensions provided in assertion response')
    else:
        results = read_extensions_from(extensions)
        for name, data in results:
            logger.info('%s: %s', name, data)
        validate_extensions_for(extensions, AUTHENTICATION_FLOW)

    # 3. Complete authentication ceremony (validates signature, challenge, origin)
    logger.debug('Calling server.authenticate_complete for user=%s', username)
    auth_data = server.authenticate_complete(
        state,  # from JWT
        [stored['credential_data']],
        assertion,  # raw browser response (WebAuthn assertion)
    )
    logger.debug('authenticate_complete succeeded for user=%s', username)

    # 4. Update stored signature counter (prevents cloned credential replay)
    if hasattr(auth_data, 'new_sign_count'):
        update_sign_count(credential_id, auth_data.new_sign_count)
        logger.info('Updated sign count to %s for user=%s', getattr(auth_data, 'new_sign_count', None), username)

    logger.info('AUTHENTICATION SUCCESS for %s', username)
    return True
