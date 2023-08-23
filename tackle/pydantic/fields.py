"""
NOTE: This is a copy of pydantic.fields.Field - See below

We have a few other fields in tackle that in order to support proper typing, we maintain
a this snippet from pydantic with what we want.
"""

import typing
from typing import Any
from typing_extensions import Unpack

from pydantic import AliasPath, AliasChoices
from pydantic import Field as PydanticField
from pydantic.fields import _EmptyKwargs, _Unset
from pydantic_core import PydanticUndefined


def Field(
        default: Any = PydanticUndefined,
        *,
        default_factory: typing.Callable[[], Any] | None = _Unset,
        alias: str | None = _Unset,
        alias_priority: int | None = _Unset,
        validation_alias: str | AliasPath | AliasChoices | None = _Unset,
        serialization_alias: str | None = _Unset,
        title: str | None = _Unset,
        description: str | None = _Unset,
        examples: list[Any] | None = _Unset,
        exclude: bool | None = _Unset,
        discriminator: str | None = _Unset,
        json_schema_extra: dict[str, Any] | typing.Callable[
            [dict[str, Any]], None] | None = _Unset,
        frozen: bool | None = _Unset,
        validate_default: bool | None = _Unset,
        repr: bool = _Unset,
        init_var: bool | None = _Unset,
        kw_only: bool | None = _Unset,
        pattern: str | None = _Unset,
        strict: bool | None = _Unset,
        gt: float | None = _Unset,
        ge: float | None = _Unset,
        lt: float | None = _Unset,
        le: float | None = _Unset,
        multiple_of: float | None = _Unset,
        allow_inf_nan: bool | None = _Unset,
        max_digits: int | None = _Unset,
        decimal_places: int | None = _Unset,
        min_length: int | None = _Unset,
        max_length: int | None = _Unset,
        # Tackle kwargs
        render_by_default: bool | None = _Unset,
        render_exclude: int | None = _Unset,
        **extra: Unpack[_EmptyKwargs],
):
    """
    Wrapper around pydantic.fields.Field to make tackle options typed as any extra
     kwargs come through in extra anyways.
    """
    return PydanticField(
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        validation_alias=validation_alias,
        serialization_alias=serialization_alias,
        title=title,
        description=description,
        examples=examples,
        exclude=exclude,
        discriminator=discriminator,
        json_schema_extra=json_schema_extra,
        frozen=frozen,
        validate_default=validate_default,
        repr=repr,
        init_var=init_var,
        kw_only=kw_only,
        pattern=pattern,
        strict=strict,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
        # Tackle items
        render_by_default=render_by_default,
        render_exclude=render_exclude,
        **extra,
    )
