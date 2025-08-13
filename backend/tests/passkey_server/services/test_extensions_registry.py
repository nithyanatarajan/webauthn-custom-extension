import pytest

from passkey_server.exceptions.errors import ExtensionValidationError
from passkey_server.services import extensions_registry as reg


def names_of(funcs: list[dict]) -> list[str]:
    return [f.get('name') for f in funcs]


def test_get_extension_functions_registration_order_and_deepcopy():
    # Sanity: expected names for registration flow in registry order
    funcs1 = reg.get_extension_functions(reg.REGISTRATION_FLOW)
    assert names_of(funcs1) == ['timeInfo', 'deviceInfo', 'someOtherExtension']

    # Ensure deep copy: mutate returned structure and ensure subsequent calls are unaffected
    # timeInfo has no metadata in the registry; we'll add one in the copy
    funcs1[0]['metadata'] = {'foo': 'bar'}

    # Also ensure objects are not same as registry objects (defensive check)
    # Build name -> original object map from the private registry
    original_by_name = {e['name']: e for e in reg._extension_functions}
    for f in funcs1:
        assert f is not original_by_name[f['name']]

    # Fetch again and verify no leaked mutation
    funcs2 = reg.get_extension_functions(reg.REGISTRATION_FLOW)
    assert names_of(funcs2) == ['timeInfo', 'deviceInfo', 'someOtherExtension']
    # timeInfo should not have the injected metadata
    assert 'metadata' not in funcs2[0]


def test_get_extension_functions_unknown_flow_raises():
    with pytest.raises(ExtensionValidationError) as exc:
        reg.get_extension_functions('NOT_A_FLOW')
    assert 'Unknown flow' in str(exc.value)
    assert 'NOT_A_FLOW' in str(exc.value)


def test_get_extension_functions_flow_references_unknown_extensions(monkeypatch):
    # Create a new flow referencing non-existent names
    bad_flow = 'BROKEN_FLOW'
    monkeypatch.setitem(reg._extension_flows, bad_flow, {'timeInfo', 'nonExistent', 'zzz'})

    with pytest.raises(ExtensionValidationError) as exc:
        reg.get_extension_functions(bad_flow)

    msg = str(exc.value)
    # Should list the missing extension names sorted
    assert 'nonExistent' in msg and 'zzz' in msg
    # Ensure the known one is not flagged as missing
    assert 'timeInfo' not in msg


def test_get_available_extensions_registration_wraps_with_customData():
    result = reg.get_available_extensions(reg.REGISTRATION_FLOW)
    assert set(result.keys()) == {reg._custom_data_key}
    funcs = result[reg._custom_data_key]
    assert names_of(funcs) == ['timeInfo', 'deviceInfo', 'someOtherExtension']


def test_get_available_extensions_authentication_wraps_with_customData():
    result = reg.get_available_extensions(reg.AUTHENTICATION_FLOW)
    assert set(result.keys()) == {reg._custom_data_key}
    funcs = result[reg._custom_data_key]
    assert names_of(funcs) == ['deviceInfo', 'anotherExtension']
