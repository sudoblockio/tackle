from tackle import Context, DocumentValueType


def string_value_macro(
        context: 'Context',
        value: 'DocumentValueType',
) -> 'DocumentValueType':
    return value


def list_value_macro(
        context: 'Context',
        value: 'DocumentValueType',
) -> 'DocumentValueType':
    return value


def dict_value_macro(
        context: 'Context',
        value: 'DocumentValueType',
) -> 'DocumentValueType':
    return value


def value_macro(
        context: 'Context',
        value: 'DocumentValueType',
) -> 'DocumentValueType':
    if isinstance(value, str):
        return string_value_macro(context=context, value=value)
    elif isinstance(value, dict):
        return dict_value_macro(context=context, value=value)
    elif isinstance(value, list):
        return list_value_macro(context=context, value=value)
    return value
