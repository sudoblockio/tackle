from types import UnionType
from typing import Any, List, _GenericAlias, _UnionGenericAlias

from pydantic.fields import FieldInfo


def type_to_string(type_: type) -> str:
    if type_ == Any:
        output = 'Any'
    elif isinstance(type_, _UnionGenericAlias):
        output = type_.__repr__()
    elif isinstance(type_, _GenericAlias):
        if isinstance(type_, List):
            output = 'list'
        else:
            output = type_.__repr__()
    elif isinstance(type_, UnionType):
        if isinstance(type_, List):
            output = 'list'
        else:
            output = type_.__repr__()
    else:
        output = type_.__name__
    if 'typing.' in output:
        output = output.replace('typing.', '')
    return output


def field_to_string(field: FieldInfo) -> str:
    """
    Convert hook ModelField type_ to string. This is used in a couple places such as
     the help dialogue and local documentation hooks.
    """
    if isinstance(field.json_schema_extra, dict) and 'type' in field.json_schema_extra:
        # We have a declarative hook type
        return field.json_schema_extra['type']
    type_ = field.annotation
    return type_to_string(type_=type_)
