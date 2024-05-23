import datetime as datetime_types
import enum
import ipaddress as ipaddress_types
import pydoc
import re
import typing
import typing as typing_types
from copy import deepcopy
from functools import partial, partialmethod
from typing import Annotated, Any, Callable, Optional, Type, TypeVar, Union

from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    PlainSerializer,
    ValidationError,
    ValidationInfo,
    WrapValidator,
)
from pydantic import networks as pydantic_network_types
from pydantic import types as pydantic_types
from pydantic.fields import FieldInfo

from tackle import Context, exceptions
from tackle.factory import new_context_from_context
from tackle.macros.hook_macros import hook_macros
from tackle.models import (
    AnyHookType,
    BaseHook,
    CompiledHookType,
    DclHookInput,
    HookFieldValidator,
    LazyBaseHook,
)
from tackle.pydantic.config import DclHookModelConfig
from tackle.pydantic.create_model import create_model
from tackle.pydantic.field_types import FieldInput
from tackle.render import render_variable
from tackle.types import DocumentType, DocumentValueType
from tackle.utils.render import wrap_jinja_braces


def parse_tmp_context(context: 'Context', element: Any, existing_context: dict):
    """
    Parse an arbitrary element. Only used for declarative hook field defaults and in
     the `run_hook` hook in the tackle provider.
    """
    tmp_context = new_context_from_context(context=context)
    tmp_context.key_path = ['->']
    tmp_context.key_path_block = ['->']

    return get_public_data_from_walk(context=tmp_context, value=element)


def dcl_hook_exec(
    hook: 'BaseHook',  # This is basically `self` in the class method
    input_element: Union[list, dict],
    context: 'Context',  # This is injected
) -> Any:
    """
    Run a declarative hook's `exec` logic which is a partial_method that is dynamically
     set on a declarative hook when the hook is created. First checks if there is some
     data to parse (the exec methods data) and if it doesn't exist, just return the
     fields of the hook. It then parses the data since it exists and then returns the
     public data or if there is a `return` field defined in the hook, just return that
     field.
    """
    if input_element is None:
        # No `exec` method so we'll just be returning the included fields from model
        return hook.model_dump(include=hook.hook_field_set, warnings=False)
    elif not isinstance(input_element, (list, dict)):
        input_element = {'returns->': input_element}

    # We have exec data so we need to parse that which will be the return of the hook
    if context.data.public and isinstance(context.data.public, dict):
        # Move the public data to an existing context
        existing_data = context.data.public.copy()
    else:
        existing_data = {}

    for field in hook.hook_field_set:
        value = hook.model_fields[field]
        # Update a function's existing context with the already matched args
        if isinstance(value, dict) and '->' in value:
            # For when the default has a hook in it
            output = parse_tmp_context(
                context=context,
                element={field: value},
                existing_context=existing_data,
            )
            existing_data.update(output)
            try:
                input_element[field] = output[field]
            except KeyError:
                raise exceptions.DclHookCallException(
                    f"Error parsing declarative hook field='{field}'. Must produce an "
                    f"output for the field's default.",
                    context=context,
                    hook_name=hook.hook_name,
                ) from None
        else:
            # Otherwise just the value itself
            existing_data.update({field: getattr(hook, field)})

    hook_context = new_context_from_context(
        context=context,
        existing_data=existing_data,
        # Pass the source and hooks because we are still in the same file
        _hooks=context.hooks,
        _source=context.source,
    )

    tmp_key = None
    if isinstance(input_element, dict):
        if '->' in input_element:
            tmp_key = hook.hook_name
            # Will de-index when outputing the public data
            input_element = {tmp_key: input_element}
        if '_>' in input_element:
            # Doesn't return anything
            input_element = {tmp_key: input_element}

    hook_context.data.input = input_element
    public_data = get_public_data_from_walk(context=hook_context, value=input_element)
    if tmp_key:
        return public_data[tmp_key]
    return public_data


def hook_extends_merge_hook(
    context: 'Context',
    hook_name: str,
    hook_input: DclHookInput,
    extends: str,
):
    """
    Core of `extends` capability of hooks which takes a reference to a hook and merges
     that hook's fields with the base hook while not overriding any fields or methods
     from the base. Methods are passed for declarative hooks but not python hooks.
    """
    base_hook = get_hook_from_context(
        context=context,
        hook_name=extends,
        # TODO: this would change if allowing extends to get instantiated with
        #  actual vars. Should be done when allowing dicts for extends.
        args=[],
    )
    if base_hook is None:
        raise exceptions.MalformedHookFieldException(
            f"In the declarative hook `{hook_name}`, the 'extends' reference to "
            f"`{extends}` can not be found.",
            hook_name=hook_name,
            context=context,
        ) from None

    # Merge fields
    if 'hook_field_set' in base_hook.model_fields:
        # We have a declarative base
        for field_name in base_hook.model_fields['hook_field_set'].default:
            if field_name not in hook_input.model_extra:
                hook_input.model_extra[field_name] = base_hook.model_fields[field_name]
            else:
                pass
    else:
        # We have a python base
        for k, v in base_hook.model_fields.items():
            if k in BaseHook.model_fields:
                # Skip base fields
                continue
            if k not in hook_input.model_extra:
                hook_input.model_extra[k] = v

        for mn in base_hook.__public_methods__:
            hook_input.public_methods[mn] = getattr(base_hook, mn)
        for mn in base_hook.__private_methods__:
            hook_input.private_methods[mn] = getattr(base_hook, mn)

        if hasattr(base_hook, 'exec'):
            hook_input.exec_ = base_hook.exec

    # Merge methods
    if 'hook_method_set' in base_hook.model_fields:
        # We are in a dcl hook - python hook
        for field_name in base_hook.model_fields['hook_method_set'].default:
            if field_name not in hook_input.model_fields:
                hook_input.model_extra[field_name] = base_hook.model_fields[field_name]


def hook_extends(
    context: 'Context',
    hook_name: str,
    hook_input: DclHookInput,
):
    """
    Implement the `extends` functionality which takes either a string reference or list
     of string references to python / declarative hooks whose fields will be merged.
    """
    if hook_input.extends is None:
        return hook_input

    elif isinstance(hook_input.extends, str):
        return hook_extends_merge_hook(
            context=context,
            hook_name=hook_name,
            hook_input=hook_input,
            extends=hook_input.extends,
        )

    elif isinstance(hook_input.extends, list):
        for i in hook_input.extends:
            if not isinstance(i, str):
                break
            return hook_extends_merge_hook(
                context=context,
                hook_name=hook_name,
                hook_input=hook_input,
                extends=i,
            )
    raise exceptions.MalformedHookFieldException(
        "The field `extends` can only be a string or list of string references to "
        "hooks to merge together.",
        context=context,
        hook_name=hook_name,
    ) from None


LITERAL_TYPES: set = {'str', 'int', 'float', 'bool', 'dict', 'list'}  # strings to match
LOOKUP_TYPES: dict = {
    'union': typing.Union,
    'optional': typing.Optional,
}
GenericFieldType = TypeVar('GenericFieldType')  # noqa


def get_hook_field_type_from_str(
    context: Context,
    hook_name: str,
    type_str: str,
) -> GenericFieldType | None:
    """
    Get the type from a field's type string and raise an error if the type is unknown.
     Supports the following types:

     - literal - ie str, int, float, list, dict
     - ipaddress - IPv4Address, IPv6Address - https://docs.python.org/3/library/ipaddress.html
     - datetime - datetime, time - https://docs.python.org/3/library/datetime.html
     - pydantic - Base64Str - https://docs.pydantic.dev/latest/api/types/
     - pydantic network - PostgresDsn - https://docs.pydantic.dev/latest/api/networks/
     - Tackle Hooks - Either python or decalarative

     Raises an error if the type is not found.
    """

    def annotate_string_serializer(type_: GenericFieldType):
        """Add a custom serializer to the type."""
        return Annotated[type_, PlainSerializer(lambda x: str(x), return_type=str)]

    if type_str in LITERAL_TYPES:
        # Treat it as a plain name - Safe to eval as type_str is always a literal type
        return eval(type_str)
    if type_str in LOOKUP_TYPES:
        return LOOKUP_TYPES[type_str]
    if hasattr(typing_types, type_str):
        return getattr(typing_types, type_str)
    elif hasattr(ipaddress_types, type_str):
        return annotate_string_serializer(getattr(ipaddress_types, type_str))
    elif hasattr(datetime_types, type_str):
        return annotate_string_serializer(getattr(datetime_types, type_str))
    elif hasattr(pydantic_types, type_str):
        return getattr(pydantic_types, type_str)
    elif hasattr(pydantic_network_types, type_str):
        return annotate_string_serializer(getattr(pydantic_network_types, type_str))

    # Finally check if it's a hook
    Hook = get_hooks_from_namespace(context=context, hook_name=type_str)
    if Hook is None:
        raise exceptions.MalformedHookFieldException(
            f"The type `{type_str}` is not recognized. Must be in python's "
            f"`typing` module, pydantic types, datetime, ipaddress, or a "
            f"tackle hook.",
            context=context,
            hook_name=hook_name,
        ) from None
    elif isinstance(Hook, LazyBaseHook):
        # We have a hook we need to build
        raise Exception("Should never happen...")
    else:
        return Hook


def parse_hook_type(
    context: Context,
    hook_name: str,
    type_str: str,
) -> GenericFieldType:
    """
    Parse a declarative hook's field's `type` string and return a python type. Supports
     complex types such as `dict[str, str]. This function uses recursion to break up
     types with brackets and compose the type offloading single types to another
     function, `get_hook_field_type_from_str`.
    """
    type_str = type_str.strip()
    # Check if it's a generic type with type arguments
    if '[' in type_str:
        # Strip the brackets. Base type will then have subtypes
        base_type_str, type_args_str_raw = type_str.split('[', 1)
        type_args_str = type_args_str_raw.rsplit(']', 1)[0]
        # Get list of types separated by commas but not within brackets.
        # ie `'dict[str, Base], Base'` -> `['dict[str, Base]', 'Base']`
        type_args = [
            parse_hook_type(
                context=context,
                hook_name=hook_name,
                type_str=arg,
            )
            for arg in re.split(r',(?![^[\]]*])', type_args_str)
        ]
        # Get base type
        base_type = parse_hook_type(
            context=context,
            hook_name=hook_name,
            type_str=base_type_str,
        )

        if len(type_args) == 0:
            return base_type
        elif base_type == Optional:
            # Optional only takes a single arg
            if len(type_args) == 1:
                return base_type[type_args[0]]
            else:
                raise exceptions.MalformedHookFieldException(
                    "The type `Optional` only takes one arg.",
                    context=context,
                    hook_name=hook_name,
                ) from None
        else:
            return base_type[tuple(type_args)]
    elif '|' in type_str:
        type_args = [
            parse_hook_type(
                context=context,
                hook_name=hook_name,
                type_str=arg,
            )
            for arg in re.split(r'\|', type_str)
        ]
        return Union[tuple(type_args)]

    # Return a string type (ie single value / not complex)
    return get_hook_field_type_from_str(context, hook_name=hook_name, type_str=type_str)


def create_validator_field_type(
    context: 'Context',
    hook_validator: HookFieldValidator,
    field_type: GenericFieldType,
    key: str,
) -> GenericFieldType:
    """
    Create a validator field type by composing a functional validator with the required
     parameters needed to parse the validator's body which is returned by the validator.
     Does this by creating a function that has the parameters injected into it via
     functools.partial for creating a temporary data needed for rendering. Associates
     this function with pydantic's functional validator with an expected function
     signature of f[Any, ValidationInfo].

     See https://docs.pydantic.dev/latest/api/functional_validators/ for more
     information on functional validators.
    """

    def validator_func(
        context: Context,
        hook_validator: HookFieldValidator,
        key: str,
        v: Any,
        info: ValidationInfo,
    ):
        # Inject the field names and values into existing context
        tmp_context = new_context_from_context(context=context)
        tmp_context.data.existing[hook_validator.field_names.value] = v
        if hook_validator.field_names.value == 'v':
            # The default is `v` but it is easier to just think of it as the field name
            tmp_context.data.existing[key] = v
        tmp_context.data.existing[hook_validator.field_names.info] = info.data

        # Walk the body and return the public data
        return get_public_data_from_walk(context=tmp_context, value=hook_validator.body)

    if hook_validator.mode == 'before':
        ValidatorType = BeforeValidator
    elif hook_validator.mode == 'after':
        ValidatorType = AfterValidator
    elif hook_validator.mode == 'wrap':
        ValidatorType = WrapValidator
    else:
        raise "This should never happen..."

    # Create a partial callable with the only parameters missing required by pydantic
    # to match the expected function signature of the validator
    wrapped_validator_func = partial(
        validator_func,
        context,
        hook_validator,
        key,
    )

    # Return the functional validator
    return Annotated[field_type, ValidatorType(wrapped_validator_func)]


def create_hook_field_validator(
    context: Context,
    hook_name: str,
    key: str,
    value: dict,
    validator_field: str | dict,
) -> GenericFieldType:
    """
    Creates a validator by parsing a hook fields `validator` key and does some light
     validation to allow ergonmic usage before assembling the validator itself in
     `create_validator_field_type`. Two types of validator forms are accepted,
     compact and expanded. See docs for details.
     TODO: Link to docs
    """
    if 'type' in value:
        field_type = parse_hook_type(context, hook_name, value['type'])
    else:
        field_type = Any

    if not isinstance(validator_field, dict):
        raise exceptions.MalformedHookFieldException(
            f"The validator in key={key} must be a dict.",
            context=context,
            hook_name=hook_name,
        )

    try:
        hook_validator = HookFieldValidator(**validator_field)
    except ValidationError as e:
        raise exceptions.MalformedHookFieldException(
            f"The key=`{key}` in the hook=`{hook_name}` has a malformed validator "
            f"field. \n{e}",
            context=context,
            hook_name=hook_name,
        )
    if hook_validator.model_extra != {} and hook_validator.body is not None:
        raise exceptions.MalformedHookFieldException(
            f"The validator field at key=`{key}` must either have a `body` field or "
            f"or just have the body as the value itself, not both. Got:\n"
            f"{list(hook_validator.model_extra.keys())}\nShould only have\n"
            f"{list(hook_validator.__dict__.keys())}",
            context=context,
            hook_name=hook_name,
        )

    if hook_validator.body is None:
        hook_validator.body = hook_validator.model_extra

    if not isinstance(hook_validator.body, dict):
        raise exceptions.MalformedHookFieldException(
            f"The validator body in the field={key} must be a map.",
            context=context,
            hook_name=hook_name,
        )
    return create_validator_field_type(
        context=context,
        hook_validator=hook_validator,
        field_type=field_type,
        key=key,
    )


def get_public_data_from_walk(context: 'Context', value: DocumentType) -> DocumentType:
    """Traverse the value and return the public data."""
    from tackle.parser import walk_document

    walk_document(context=context, value=value)
    return context.data.public


def create_default_factory(
    context: Context,
    hook_name: str,
    value: dict,
    value_is_factory: bool = False,
):
    """
    Create a default_factory field out of the value which is a callable that parses the
     data calling hooks if they exist.
    """
    if value_is_factory:
        default_factory = value
    else:
        default_factory = value.pop('default_factory')

    if not isinstance(default_factory, (dict, list)):
        raise exceptions.MalformedHookFieldException(
            "The default_factory must be a string (compact hook call), "
            "dict, or list which will be parsed.",
            context=context,
            hook_name=hook_name,
        )

    # Create a callable from a dict which walks the data and returns the public data
    # from execution. Is used in default_factory which expects a callable with no args.
    tmp_context = new_context_from_context(
        context=context,
        _hooks=context.hooks,
        _source=context.source,
    )
    value['default_factory'] = partial(
        get_public_data_from_walk, tmp_context, default_factory
    )


def update_field_dict_with_type(
    context: 'Context',
    hook_name: str,
    key: str,
    value: DocumentValueType,
    field_dict: dict,
):
    """
    Update a hook's field dict with a tuple[Type, Field] which is used when creating
     a hook through pydantic's create_model function. Also creates the associated
     callables for default_factories and validators per the spec of a pydantic field.
    """
    # Render `enum` field if string which is a special case
    if 'enum' in value and isinstance(value['enum'], str):
        value['enum'] = render_variable(context, wrap_jinja_braces(value['enum']))

    if 'default_factory' in value:
        create_default_factory(context, hook_name=hook_name, value=value)

    try:
        field_input = FieldInput(**value)
    except ValidationError as e:
        raise exceptions.MalformedHookFieldException(
            e,
            context=context,
            hook_name=hook_name,
        )

    if field_input.enum is not None:
        if field_input.type:
            # TODO: Allow `enum` to be a type
            #  https://github.com/sudoblockio/tackle/issues/187
            raise exceptions.MalformedHookFieldException(
                "Enums are implicitly typed. Future version will have "
                "option to have enums as types.",
                context=context,
                hook_name=hook_name,
            )
        enum_type = enum.Enum(key, {i: i for i in field_input.enum})
        if field_input.default:
            field_dict[key] = (enum_type, field_input.default)
        else:
            field_dict[key] = (enum_type, ...)
    else:
        if field_input.description:
            field_input.description = field_input.description.__repr__()

        field_type = parse_hook_type(
            context=context,
            type_str=field_input.type,
            hook_name=hook_name,
        )

        if field_input.validator:
            field_type = create_hook_field_validator(
                context=context,
                hook_name=hook_name,
                key=key,
                value=value,
                validator_field=field_input.validator,
            )
        # Create the field
        field_dict[key] = (field_type, Field(**value))


def create_dcl_hook_fields(
    context: Context,
    hook_input: DclHookInput,
    hook_name: str,
) -> (dict[str, tuple], set[str], set[str]):
    """
    Parses the field inputs for a declarative hook by checking if they are methods or
     just fields. Builds sets of both the field and method names and returns that with
     a dict of the field data used to instantiate a new hook.
    """
    field_dict: dict[str, tuple] = {}
    hook_field_set: set[str] = set()
    hook_method_set: set[str] = set()
    for k, v in hook_input.model_extra.items():
        if isinstance(v, FieldInfo):
            if v.annotation == Callable:
                # TODO: RM methods
                hook_method_set.add(k)
            field_dict[k] = (v.annotation, v)
        elif '<-' in v:
            # Raw public method
            field_dict[k] = (
                Callable,
                LazyBaseHook(
                    hook_name=k,
                    input_raw=v['<-'],
                    is_public=True,
                ),
            )
            hook_method_set.add(k)
            continue
        elif '<_' in v:
            # Raw private method
            field_dict[k] = (
                Callable,
                LazyBaseHook(
                    hook_name=k,
                    input_raw=v['<_'],
                    is_public=False,
                ),
            )
            hook_method_set.add(k)
            continue
        elif isinstance(v, dict):
            # Dict types are special as they include field information such as `type`
            update_field_dict_with_type(
                context=context,
                key=k,
                value=v,
                hook_name=hook_name,
                field_dict=field_dict,
            )
        elif isinstance(v, str) and v in LITERAL_TYPES:
            # Input of form `foo: str|int|list...` which means it is typed and required
            field_dict[k] = (pydoc.locate(v).__name__, Field(...))
        elif isinstance(v, (str, int, float, bool, list, dict)):
            # Input of form `foo: some_value` so we infer type and give default value
            field_dict[k] = (type(v), Field(v))
        elif isinstance(v, LazyBaseHook):
            # Is encountered when inheritance is imposed and calling function methods
            # TODO: Missing hook_method_set.add(k)?
            field_dict[k] = (Callable, v)
        else:
            raise Exception("This should never happen")
        hook_field_set.add(k)
    return field_dict, hook_field_set, hook_method_set


def new_dcl_hook_input(
    context: 'Context',
    hook_name: str,
    hook_input_dict: dict | str,
) -> DclHookInput:
    """
    Create the hook_input which are keys supplied in the hook definition that inform how
     the hook should be compiled. All the fields are serialized with the extra vars
     being the inputs to the hook.
    """
    try:
        return DclHookInput(**hook_input_dict)
    except ValidationError as e:
        raise exceptions.HookParseException(
            f"Invalid input for creating hook=`{hook_name}`. \n {e}", context=context
        )


def get_model_config_from_hook_input(
    context: Context,
    hook_name: str,
    hook_input_dict: dict,
) -> DclHookModelConfig | None:
    """If the `model_config` field is declared, pop it off and return an object."""
    if 'model_config' in hook_input_dict:
        model_config = hook_input_dict.pop('model_config')
        try:
            return DclHookModelConfig(**model_config)
        except ValidationError as e:
            raise exceptions.MalformedHookFieldException(
                e, context=context, hook_name=hook_name
            )


# def update_hook_input_validators(
#         context: 'Context',
#         hook_input: DclHookInput,
#         hook_name: str,
# ):
#     """
#     TODO: Support validator field
#      https://github.com/sudoblockio/tackle/issues/221
#     """
#     if hook_input.model_fields['validators'].default is not None:
#         raise NotImplementedError
#     # Validators
#     for k, v in hook_input.validators.items():
#         if k not in hook_input.hook_fields_:
#             raise exceptions.MalformedHookDefinitionException(
#                 f"In the hook definition `{hook_name}`, the field `validators` must be "
#                 f" map keyed on a field name to apply the validator. Available keys:"
#                 f" {','.join([k for k, _ in hook_input.hook_fields_.items()])}",
#                 context=context, hook_name=hook_name
#             )
#         # TODO: Create callable with normal rigging
#         raise NotImplementedError


def create_dcl_hook(
    context: 'Context',
    hook_name: str,
    hook_input_raw: dict | str,
) -> 'CompiledHookType':
    """
    Create a model from the hook input dict. Calls numerous functions to upgrade the
     hook input dict including:

    - A macro to expand all the keys so that they can be easily parsed
    - Pulling out model_config and validator keys
    - Validating the base field inputs (ie `type` etc)
    - Implementing inheritance through the `extends` key
    - Finalizing all fields and methods as a dict of tuples
    - Creating a new hook through pydantic's create_model function
    """
    # Macro to expand all keys properly so that a field's default can be parsed
    hook_input_dict = hook_macros(
        context=context,
        hook_input_raw=hook_input_raw,
        hook_name=hook_name,
    )

    # Pull out the model_config if it exists
    model_config = get_model_config_from_hook_input(context, hook_name, hook_input_dict)
    # # TODO: Apply validators
    # update_hook_input_validators(context, hook_input=hook_input, hook_name=hook_name)

    # Serialize known inputs
    hook_input = new_dcl_hook_input(context, hook_name, hook_input_dict=hook_input_dict)
    # Implement inheritance
    hook_extends(context, hook_name, hook_input=hook_input)

    # First pass through the func_dict to parse out the methods and build a dict of
    # field types along with their special fields such as default_factory and validator
    # which are callables.
    field_dict, hook_field_set, hook_method_set = create_dcl_hook_fields(
        context=context,
        hook_input=hook_input,
        hook_name=hook_name,
    )
    # # Apply overrides to hook_input_raw
    # hook_input_dict = update_input_dict(
    #     input_dict=hook_input_dict,
    #     update_dict=context.data.overrides,
    # )

    hook_input_field_dict = {
        k: (v.annotation, FieldInfo(default=getattr(hook_input, k), exclude=True))
        for k, v in hook_input.model_fields.items()
    }

    # Create a function with the __module__ default to pydantic.main
    try:
        Hook = create_model(
            hook_name,
            __base__=BaseHook,
            __config__=model_config,
            # TODO: RM this and overlay validators from field def on funcational field
            #  field validators?
            # __validators__=hook_input.validators,
            # hook_name=(typing.ClassVar[str], FieldInfo(default=hook_name, exclude=True)),
            hook_name=(typing.ClassVar[str], hook_name),
            hook_field_set=(set, FieldInfo(default=hook_field_set, exclude=True)),
            hook_method_set=(set, FieldInfo(default=hook_method_set, exclude=True)),
            **field_dict,
            **hook_input_field_dict,
        )
    except NameError as e:
        if 'shadows a BaseModel attribute' in e.args[0]:
            shadowed_arg = e.args[0].split('\"')[1]
            extra = "a different value"
            raise exceptions.ShadowedHookFieldException(
                f"The function field \'{shadowed_arg}\' is reserved. Use {extra}.",
                hook_name=hook_name,
                context=context,
            ) from None
        # Don't know what else could happen
        raise e
    except Exception as e:
        raise e

    for method_name, method in hook_input.public_methods.items():
        setattr(Hook, method_name, method)
        Hook.__public_methods__.append(method_name)

    for method_name, method in hook_input.private_methods.items():
        setattr(Hook, method_name, method)
        Hook.__private_methods__.append(method_name)

    # Create an 'exec' method on the function that can be called later.
    if isinstance(hook_input.exec_, Callable):
        setattr(Hook, 'exec', hook_input.exec_)
    else:
        setattr(Hook, 'exec', partialmethod(dcl_hook_exec, hook_input.exec_))

    # TODO: Rm when filters fixed
    # context.env_.filters[func_name] = Hook(
    #     existing_data={},
    #     no_input=context.no_input,
    # ).wrapped_exec

    return Hook


def create_dcl_method(
    context: 'Context',
    Hook: AnyHookType,
    arg: str,
) -> CompiledHookType:
    """Upgrade a declarative hook method."""
    # method_raw will still have the arrow as the first key
    method = Hook.model_fields[arg].default

    # Update method with values from base class so that fields can be inherited
    # from the base hook. function_fields is a list of those fields that aren't
    # methods / special vars (ie args, return, etc).
    for i in Hook.model_fields['hook_field_set'].default:
        # Base method should not override child.
        if i not in method.input_raw:
            method.input_raw[i] = Hook.model_fields[i]

    return create_dcl_hook(
        context=context,
        hook_name=arg,
        hook_input_raw=method.input_raw,
    )


def enrich_hook(
    context: 'Context',
    Hook: CompiledHookType,
    args: list,
) -> CompiledHookType:
    """
    Take a hook and enrich it by lining up the args with potential methods / hook args /
     kwargs. For methods, it recognizes the arg is a method, compiles the method hook
     with the attributes of the base hook making it inherit them.
    """
    # Handle args
    for n, arg in enumerate(args):
        # When arg inputs are not hashable then they are actual arguments which will be
        # consumed later
        if isinstance(arg, (list, dict)):
            # TODO: Check how this logic works with `args` condition below which works
            #  for bypassing the processing of args for later logic
            pass
        # If arg in methods, compile hook
        elif arg in Hook.model_fields and Hook.model_fields[arg].annotation == Callable:
            Hook = create_dcl_method(context=context, Hook=Hook, arg=args.pop(0))
            if len(args) != 0:
                # Recurse if we have more args
                return enrich_hook(
                    context=context,
                    Hook=Hook,
                    args=args,
                )
        elif 'args' in Hook.model_fields:
            # The hook takes positional args
            pass
        else:
            raise exceptions.UnknownHookInputArgumentException(
                f"Unknown arg supplied `{arg}`",
                context=context,
                hook_name=Hook.hook_name.default,
            )
    return Hook


def get_hooks_from_namespace(
    context: 'Context',
    hook_name: str,
) -> CompiledHookType | None:
    """Get the public, private, or native hook from the context."""
    if hook_name == '_default':
        return context.hooks.default

    for ns in ['public', 'private', 'native']:
        hook_space = getattr(context.hooks, ns)
        Hook = hook_space.get(hook_name, None)
        if Hook is not None:
            if isinstance(Hook, LazyBaseHook):
                Hook = create_dcl_hook(
                    context=context,
                    hook_name=hook_name,
                    hook_input_raw=deepcopy(Hook.input_raw),
                )
            return Hook


def get_hook_from_context(
    context: 'Context',
    hook_name: str,
    args: list,
    throw: bool = False,
) -> Optional[CompiledHookType]:
    """
    Gets the hook from the context and calls enrich_hook which compiles the hook with
     its associated fields and methods.
    """
    # TODO: self
    # hook_context.hooks.private['self'] =
    Hook = get_hooks_from_namespace(context=context, hook_name=hook_name)
    if Hook is None:
        if throw:
            raise exceptions.raise_unknown_hook(context=context, hook_name=hook_name)
        return None
    # We could have a hook call with methods so need to enrich the hook
    Hook = enrich_hook(
        context=context,
        Hook=Hook,
        args=args,
    )

    # Validate the hook
    for k, v in BaseHook.model_fields.items():
        if k in Hook.model_fields:
            if Hook.model_fields[k].annotation != BaseHook.model_fields[k].annotation:
                hook_type = Hook.model_fields[k].annotation
                base_hook_type = BaseHook.model_fields[k].annotation
                raise exceptions.MalformedHookDefinitionException(
                    f"The field name=`{k}` of type={hook_type} is not the "
                    f"same type as the BaseHook's type=`{base_hook_type}`. Exiting...",
                    context=context,
                    hook_name=hook_name,
                )
    return Hook
