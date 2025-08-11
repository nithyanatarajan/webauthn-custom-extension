_custom_data_key = 'customData'
_extension_functions = [{'name': 'timeInfo'}, {'name': 'deviceInfo'}]


def get_available_extensions():
    return {_custom_data_key: _extension_functions}


def get_extensions_from(extensions):
    return [(f['name'], f.get('value') or f.get('error')) for f in extensions.get(_custom_data_key, [])]
