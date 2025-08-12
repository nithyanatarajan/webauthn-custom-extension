from unittest.mock import patch

from passkey_server.services.extensions import get_extensions_from, verify_extension


class TestGetExtensionsFrom:
    def test_returns_name_and_value_tuples(self):
        extensions = {
            'customData': [
                {'name': 'timeInfo', 'value': {'ts': 123}},
                {'name': 'deviceInfo', 'value': {'model': 'X'}},
            ]
        }
        result = get_extensions_from(extensions)
        assert ('timeInfo', {'ts': 123}) in result
        assert ('deviceInfo', {'model': 'X'}) in result
        assert len(result) == 2

    def test_uses_error_when_value_missing(self):
        extensions = {
            'customData': [
                {'name': 'timeInfo', 'error': 'denied'},
                {'name': 'deviceInfo', 'value': None, 'error': 'not available'},
            ]
        }
        # Note: f.get('value') or f.get('error') selects error when value falsy
        result = get_extensions_from(extensions)
        assert ('timeInfo', 'denied') in result
        # value None is falsy, so should fall back to error
        assert ('deviceInfo', 'not available') in result
        assert len(result) == 2

    def test_missing_custom_data_key_returns_empty_list(self):
        assert get_extensions_from({}) == []

    def test_empty_list_returns_empty(self):
        assert get_extensions_from({'customData': []}) == []


class TestVerifyExtension:
    def test_returns_none_when_destination_not_extn(self):
        assert verify_extension({'name': 'foo'}) is None
        assert verify_extension({'name': 'bar', 'metadata': {'destination': 'CLIENT'}}) is None
        assert verify_extension({}) is None
        assert verify_extension(None) is None

    def test_calls_verify_with_metadata_path(self):
        ext = {'name': 'someOtherExtension', 'metadata': {'destination': 'EXTN', 'path': 'something'}}
        with patch('passkey_server.services.extensions.verify_extension_with_retries') as mock_verify:
            mock_verify.return_value = {'ok': True}
            result = verify_extension(ext)
            mock_verify.assert_called_once_with('something')
            assert result == {'ok': True}

    def test_calls_verify_falling_back_to_name_when_no_path(self):
        ext = {'name': 'timeInfo', 'metadata': {'destination': 'EXTN'}}
        with patch('passkey_server.services.extensions.verify_extension_with_retries') as mock_verify:
            mock_verify.return_value = {'status': 'verified'}
            result = verify_extension(ext)
            mock_verify.assert_called_once_with('timeInfo')
            assert result == {'status': 'verified'}

    def test_calls_verify_with_empty_string_when_no_path_and_no_name(self):
        ext = {'metadata': {'destination': 'EXTN'}}
        with patch('passkey_server.services.extensions.verify_extension_with_retries') as mock_verify:
            mock_verify.return_value = {'status': 'verified'}
            result = verify_extension(ext)
            mock_verify.assert_called_once_with('')
            assert result == {'status': 'verified'}
