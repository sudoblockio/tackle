from typing import Any, Callable

from pydantic import BaseModel, Field


class FieldInput(BaseModel):
    """
    Model to validate inputs into declarative hook fields. It is the model version of
     the inputs into tackle.pydantic.fields.Field for serialization purposes.
    """

    type: str | None = Field(None, description="")
    enum: list | None = Field(None, description="")
    validator: dict | None = Field(None, description="")
    validators: list[dict] | None = Field(None, description="")
    render_exclude: list | None = Field(None, description="")
    parse_keys: list | None = Field(None, description="")

    # pydantic fields
    default: Any = Field(None, description="")
    default_factory: Callable[[], Any] | None = Field(None, description="")
    # default_factory: dict | None = Field(None, description="")
    alias: str | None = Field(None, description="")
    alias_priority: int | None = Field(None, description="")
    # validation_alias: str | AliasPath | AliasChoices | None = Field(None, description="")
    validation_alias: str | None = Field(None, description="")
    serialization_alias: str | None = Field(None, description="")
    title: str | None = Field(None, description="")
    description: str | None = Field(None, description="")
    examples: list[Any] | None = Field(None, description="")
    exclude: bool | None = Field(None, description="")
    discriminator: str | None = Field(None, description="")
    json_schema_extra: dict[str, Any] | Callable[[dict[str, Any]], None] | None = Field(
        None, description=""
    )
    frozen: bool | None = Field(None, description="")
    validate_default: bool | None = Field(None, description="")
    repr: bool = Field(None, description="")
    init_var: bool | None = Field(None, description="")
    kw_only: bool | None = Field(None, description="")
    pattern: str | None = Field(None, description="")
    strict: bool | None = Field(None, description="")
    gt: float | None = Field(None, description="")
    ge: float | None = Field(None, description="")
    lt: float | None = Field(None, description="")
    le: float | None = Field(None, description="")
    multiple_of: float | None = Field(None, description="")
    allow_inf_nan: bool | None = Field(None, description="")
    max_digits: int | None = Field(None, description="")
    decimal_places: int | None = Field(None, description="")
    min_length: int | None = Field(None, description="")
    max_length: int | None = Field(None, description="")

    # Internal field to keep track of the type of field
    __hook_field_type__: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__hook_field_type__ = 'literal'
