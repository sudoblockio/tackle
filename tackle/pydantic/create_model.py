"""
NOTE: This is a copy of pydantic.main.create_model - See below

Pydantic's create model function throws an exception when a __config__ and __base__ are
supplied (see https://github.com/pydantic/pydantic/discussions/5782) so we're stuck with
this hack which is a copy of the pydantic create_model function minus the exception.

Works fine...
"""
from __future__ import annotations

import typing
import warnings
from types import prepare_class, resolve_bases
from typing import Any, Tuple, cast

from pydantic import BaseModel

if typing.TYPE_CHECKING:
    AnyClassMethod = classmethod[Any, Any, Any]
    TupleGenerator = typing.Generator[Tuple[str, Any], None, None]
    Model = typing.TypeVar('Model', bound='BaseModel')

from pydantic._internal import _config  # noqa
from pydantic.errors import PydanticUserError

# from pydantic.config import ConfigDict
from tackle.pydantic.config import DclHookModelConfig


# When updating, only copy over the function
def create_model(
    __model_name: str,
    *,
    # __config__: ConfigDict | None = None,
    __config__: DclHookModelConfig | None = None,
    __base__: type[Model] | tuple[type[Model], ...] | None = None,
    __module__: str = __name__,
    __validators__: dict[str, AnyClassMethod] | None = None,
    __cls_kwargs__: dict[str, Any] | None = None,
    __slots__: tuple[str, ...] | None = None,
    **field_definitions: Any,
) -> type[Model]:
    """
    Dynamically create a model.
    :param __model_name: name of the created model
    :param __config__: config dict/class to use for the new model
    :param __base__: base class for the new model to inherit from
    :param __module__: module of the created model
    :param __validators__: a dict of method names and @validator class methods
    :param __cls_kwargs__: a dict for class creation
    :param __slots__: Deprecated, `__slots__` should not be passed to `create_model`
    :param field_definitions: fields of the model (or extra fields if a base is supplied)
        in the format `<name>=(<type>, <default value>)` or `<name>=<default value>, e.g.
        `foobar=(str, ...)` or `foobar=123`, or, for complex use-cases, in the format
        `<name>=<Field>` or `<name>=(<type>, <FieldInfo>)`, e.g.
        `foo=Field(datetime, default_factory=datetime.utcnow, alias='bar')` or
        `foo=(str, FieldInfo(title='Foo'))`
    """
    if __slots__ is not None:
        # __slots__ will be ignored from here on
        warnings.warn('__slots__ should not be passed to create_model', RuntimeWarning)

    if __base__ is not None:
        # if __config__ is not None:
        #     raise PydanticUserError(
        #         'to avoid confusion `__config__` and `__base__` cannot be used together',
        #         code='create-model-config-base',
        #     )
        if not isinstance(__base__, tuple):
            __base__ = (__base__,)
    else:
        __base__ = (typing.cast(typing.Type['Model'], BaseModel),)

    __cls_kwargs__ = __cls_kwargs__ or {}

    fields = {}
    annotations = {}

    for f_name, f_def in field_definitions.items():
        if f_name.startswith('_'):
            warnings.warn(
                f'fields may not start with an underscore, ignoring "{f_name}"',
                RuntimeWarning,
            )
        if isinstance(f_def, tuple):
            f_def = cast('tuple[str, Any]', f_def)
            try:
                f_annotation, f_value = f_def
            except ValueError as e:
                raise PydanticUserError(
                    'Field definitions should either be a `(<type>, <default>)`.',
                    code='create-model-field-definitions',
                ) from e
        else:
            f_annotation, f_value = None, f_def

        if f_annotation:
            annotations[f_name] = f_annotation
        fields[f_name] = f_value

    namespace: dict[str, Any] = {
        '__annotations__': annotations,
        '__module__': __module__,
    }
    if __validators__:
        namespace.update(__validators__)
    namespace.update(fields)
    if __config__:
        namespace['model_config'] = _config.ConfigWrapper(__config__).config_dict
    resolved_bases = resolve_bases(__base__)
    meta, ns, kwds = prepare_class(__model_name, resolved_bases, kwds=__cls_kwargs__)
    if resolved_bases is not __base__:
        ns['__orig_bases__'] = __base__
    namespace.update(ns)
    return meta(
        __model_name,
        resolved_bases,
        namespace,
        __pydantic_reset_parent_namespace__=False,
        **kwds,
    )
