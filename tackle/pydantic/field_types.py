from pydantic import BaseModel, Field
from typing import Any, Callable, Optional


class FieldInput(BaseModel):
    """
    Model to validate inputs into declarative hook fields. It is the model version of
     the inputs into tackle.pydantic.fields.Field for serialization purposes.
    """
    type: Optional[str] = Field(None, description="")
    enum: Optional[list] = Field(None, description="")
    validator: Optional[dict] = Field(None, description="")
    validators: Optional[list[dict]] = Field(None, description="")
    render_exclude: Optional[list] = Field(None, description="")
    parse_keys: Optional[list] = Field(None, description="")

    # pydantic fields
    default: Any = Field(None, description="")
    default_factory: Optional[Callable[[], Any]] = Field(None, description="")
    # default_factory: dict | None = Field(None, description="")
    alias: Optional[str] = Field(None, description="")
    alias_priority: Optional[int] = Field(None, description="")
    # validation_alias: str | AliasPath | AliasChoices | None = Field(None, description="")
    validation_alias: Optional[str] = Field(None, description="")
    serialization_alias: Optional[str] = Field(None, description="")
    title: Optional[str] = Field(None, description="")
    description: Optional[str] = Field(None, description="")
    examples: Optional[list[Any]] = Field(None, description="")
    exclude: Optional[bool] = Field(None, description="")
    discriminator: Optional[str] = Field(None, description="")
    json_schema_extra: Optional[dict[str, Any]] = Field(None, description="")
    frozen: Optional[bool] = Field(None, description="")
    validate_default: Optional[bool] = Field(None, description="")
    repr: bool = Field(None, description="")
    init_var: Optional[bool] = Field(None, description="")
    kw_only: Optional[bool] = Field(None, description="")
    pattern: Optional[str] = Field(None, description="")
    strict: Optional[bool] = Field(None, description="")
    gt: Optional[float] = Field(None, description="")
    ge: Optional[float] = Field(None, description="")
    lt: Optional[float] = Field(None, description="")
    le: Optional[float] = Field(None, description="")
    multiple_of: Optional[float] = Field(None, description="")
    allow_inf_nan: Optional[bool] = Field(None, description="")
    max_digits: Optional[int] = Field(None, description="")
    decimal_places: Optional[int] = Field(None, description="")
    min_length: Optional[int] = Field(None, description="")
    max_length: Optional[int] = Field(None, description="")

    # Internal field to keep track of the type of field
    __hook_field_type__: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__hook_field_type__ = 'literal'
