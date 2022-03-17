from pydantic import BaseModel, create_model, Field, validator
from typing import Any, Union, Type

KWARG_TYPES: dict = {
    'str': str,
    'list': list,
    'dict': dict,
    'bool': bool,
    'int': int,
    'float': float,
}


class FuncKwarg(BaseModel):
    type_: Union[str, Type]
    description: str
    default: Any

    @validator('type_')
    def validate_type(cls, v):
        if v in KWARG_TYPES:
            return KWARG_TYPES[v]
        else:
            raise ValueError(
                f"Type {v} must be one of {','.join(list(KWARG_TYPES.keys()))}"
            )


class Func(BaseModel):
    # schema_: Dict[str, FuncKwarg] = Field(None, alias='schema')
    schema_: dict = Field(None, alias='schema')
    exec: Any = None
    args: list = None
    extends: str = None
    validators: dict = None
    methods: dict = None


def create_function_model(func_name: str, func_dict: dict):
    """
    - Take in schema and unpack into dict of tuples
    """
    func = Func(**func_dict)
    parsed_schema = {}
    for k, v in func.schema_.items():
        if isinstance(v, dict):
            parsed_schema[k] = Field(**v)
        if isinstance(v, (str, int, float, bool)):
            parsed_schema[k] = v

    return create_model(func_name, **parsed_schema)
