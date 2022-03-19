import re
from pydantic import BaseModel, create_model, Field, validator
from typing import Any, Union, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context

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


# Should be in parser
def exec_function():
    pass


