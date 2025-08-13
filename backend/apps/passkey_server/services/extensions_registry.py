import copy
import logging

from typing import Any

from passkey_server.exceptions.errors import ExtensionValidationError

logger = logging.getLogger(__name__)

_custom_data_key = 'customData'
_extension_functions: list[dict[str, Any]] = [
    {'name': 'timeInfo'},
    {'name': 'deviceInfo'},
    {'name': 'someOtherExtension', 'metadata': {'destination': 'EXTN', 'path': 'something'}},
    {'name': 'anotherExtension', 'metadata': {'destination': 'EXTN', 'path': 'anotherthing'}},
]

REGISTRATION_FLOW = 'REGISTRATION_FLOW'
AUTHENTICATION_FLOW = 'AUTHENTICATION_FLOW'
_extension_flows: dict[str, set[str]] = {
    REGISTRATION_FLOW: {'timeInfo', 'deviceInfo', 'someOtherExtension'},
    AUTHENTICATION_FLOW: {'deviceInfo', 'anotherExtension'},
}


def _require_flow(flow: str) -> set[str]:
    try:
        return _extension_flows[flow]
    except KeyError:
        raise ExtensionValidationError(f'Unknown flow: {flow!r}') from None


def get_extension_functions(flow: str) -> list[dict[str, Any]]:
    """Return deep-copied extension dicts (preserves registry order)."""
    logger.info('Fetching extensions for flow: %s', flow)
    wanted = _require_flow(flow)
    # Validate profile entries exist in the registry
    registry_names = {e['name'] for e in _extension_functions}
    unknown = wanted - registry_names
    if unknown:
        raise ExtensionValidationError(f"Flow '{flow}' references unknown extension(s): {sorted(unknown)}")
    # Keep registry order and deep-copy items
    return [copy.deepcopy(e) for e in _extension_functions if e['name'] in wanted]


def get_available_extensions(flow: str) -> dict[str, list[dict[str, Any]]]:
    funcs = get_extension_functions(flow)
    logger.info('Providing available extensions for flow: %s', [f.get('name') for f in funcs])
    return {_custom_data_key: funcs}
