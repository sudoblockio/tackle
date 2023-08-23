from pydantic import BaseModel, FieldValidationInfo

from tackle.pydantic.fields import Field

from typing import Any, Callable
from pydantic import model_validator
from pydantic.functional_validators import FieldValidatorModes
from pydantic._internal._generate_schema import GenerateSchema  # noqa

from tackle import exceptions

class DclHookValidator(BaseModel):
    fields: dict | None = Field(
        {'v': Any, 'info': FieldValidationInfo},
        description="",
    )
    mode: FieldValidatorModes = Field(
        'after',
        description="",
    )
    body: dict | list = Field(..., description="")


DclHookValidators = dict[str, Callable]

def new_dcl_hook_validator(input_value: dict | list | str) -> DclHookValidator:
    if isinstance(input_value, dict):
        validator = DclHookValidator(**input_value)
    elif isinstance(input_value, list):
        raise exceptions.UnknownInputArgumentException(
            "", context=context
        )
    return validator
