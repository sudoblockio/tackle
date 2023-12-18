from typing import Literal

from pydantic import BaseModel, Field
from pydantic._internal._generate_schema import GenerateSchema  # noqa
from pydantic.config import ExtraValues  # noqa
from pydantic.config import JsonEncoder  # noqa
from pydantic.config import JsonSchemaExtraCallable  # noqa


class DclHookModelConfig(BaseModel):
    """Declarative hook model_config inputs."""

    title: str | None = Field(None, description="")
    str_to_lower: bool = Field(False, description="")
    str_to_upper: bool = Field(False, description="")
    str_strip_whitespace: bool = Field(False, description="")
    str_min_length: int = Field(0, description="")
    str_max_length: int | None = Field(None, description="")
    extra: ExtraValues | None = Field(None, description="")
    frozen: bool = Field(False, description="")
    populate_by_name: bool = Field(False, description="")
    use_enum_values: bool = Field(False, description="")
    validate_assignment: bool = Field(False, description="")
    arbitrary_types_allowed: bool = Field(False, description="")
    from_attributes: bool = Field(False, description="")
    # whether to use the used alias (or first alias for "field required" errors) instead of field_names
    # to construct error `loc`s, default True
    loc_by_alias: bool = Field(True, description="")

    # TODO: Support this
    # alias_generator: Callable[[str], str] | None = Field(None, description="")
    ignored_types: tuple[type, ...] = Field((), description="")
    allow_inf_nan: bool = Field(True, description="")
    # json_schema_extra: dict[str, object] | JsonSchemaExtraCallable | None
    json_encoders: dict[type[object], JsonEncoder] | None = Field(None, description="")

    # new in V2
    strict: bool = Field(False, description="")
    # whether instances of models and dataclasses (including subclass instances) should re-validate, default 'never'
    revalidate_instances: Literal['always', 'never', 'subclass-instances'] = Field(
        'never', description=""
    )
    ser_json_timedelta: Literal['iso8601', 'float'] = Field('iso8601', description="")
    ser_json_bytes: Literal['utf8', 'base64'] = Field('utf8', description="")
    # whether to validate default values during validation, default False
    validate_default: bool = Field(False, description="")
    validate_return: bool = Field(False, description="")
    protected_namespaces: tuple[str, ...] = Field(('model_',), description="")
    hide_input_in_errors: bool = Field(False, description="")
    defer_build: bool = Field(False, description="")
    schema_generator: type[GenerateSchema] | None = Field(None, description="")
