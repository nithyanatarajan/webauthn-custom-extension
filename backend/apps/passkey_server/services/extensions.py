import logging

from typing import Any

from passkey_server.exceptions.errors import ExtensionValidationError
from passkey_server.services.validation import verify_extension_with_retries

from .extensions_registry import _custom_data_key, get_extension_functions

logger = logging.getLogger(__name__)


def read_extensions_from(extensions: dict[str, Any]) -> list[tuple[str, Any]]:
    items = [
        (f['name'], f.get('value') or f.get('error'))
        for f in (extensions or {}).get(_custom_data_key, []) or []
        if isinstance(f, dict) and 'name' in f
    ]
    logger.debug('Parsed %d extension result(s)', len(items))
    return items


def validate_extensions_for(extensions: dict[str, Any], flow: str) -> None:
    funcs = get_extension_functions(flow)
    required_names = [f.get('name') for f in funcs]
    provided_list = (extensions or {}).get(_custom_data_key, []) or []
    provided_names = [f.get('name') for f in provided_list if isinstance(f, dict)]

    logger.debug('Validating extensions. Required=%s Provided=%s', required_names, provided_names)

    missing = [name for name in required_names if name not in provided_names]
    if missing:
        logger.error('Missing required extensions: %s', missing)
        raise ExtensionValidationError(f'Missing required extensions: {", ".join(missing)}')

    # Server-side verification for required extensions that need it
    for ext in funcs:
        verify_extension(ext)


async def verify_extension(extension: dict[str, Any]) -> None:
    metadata = (extension or {}).get('metadata') or {}
    if metadata.get('destination') == 'EXTN':
        path = metadata.get('path') or extension.get('name') or ''
        logger.info('Verifying extension via EXT server: path=%s', path)
        return await verify_extension_with_retries(path)
    return None
