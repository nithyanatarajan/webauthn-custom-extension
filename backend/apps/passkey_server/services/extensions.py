from passkey_server.exceptions.errors import ExtensionValidationError
from passkey_server.services.validation import verify_extension_with_retries

_custom_data_key = 'customData'
_extension_functions = [
    {'name': 'timeInfo'},
    {'name': 'deviceInfo'},
    {'name': 'someOtherExtension', 'metadata': {'destination': 'EXTN', 'path': 'something'}},
]


def get_available_extensions():
    return {_custom_data_key: _extension_functions}


def get_extensions_from(extensions):
    return [(f['name'], f.get('value') or f.get('error')) for f in extensions.get(_custom_data_key, [])]


def validate_extensions(extensions: dict):
    # Ensure required extensions are present
    required_names = [f.get('name') for f in _extension_functions]
    provided_list = (extensions or {}).get(_custom_data_key, []) or []
    provided_names = [f.get('name') for f in provided_list if isinstance(f, dict)]

    missing = [name for name in required_names if name not in provided_names]
    if missing:
        raise ExtensionValidationError(f'Missing required extensions: {", ".join(missing)}')

    # Verify each extension (server-side where applicable)
    for ext in _extension_functions:
        verify_extension(ext)


def verify_extension(extension: dict):
    metadata = (extension or {}).get('metadata') or {}
    if metadata.get('destination') == 'EXTN':
        path = metadata.get('path') or extension.get('name') or ''
        return verify_extension_with_retries(path)
    return None
