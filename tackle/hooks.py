import enum
from functools import partialmethod, partial
import re
import typing
from typing import TYPE_CHECKING, Union, Any, Type, Callable, Optional
from pydantic import ValidationError, field_validator
import pydoc

from tackle import exceptions
from tackle.factory import new_context
from tackle.imports import import_with_fallback_install
from tackle.macros.hook_macros import hook_macros
from tackle.render import render_variable
from tackle.pydantic.create_model import create_model
from tackle.pydantic.field_types import FieldInput
from tackle.pydantic.fields import Field
from tackle.utils.dicts import update_input_dict
from tackle.types import DocumentValueType, DocumentType
from tackle.models import (
    BaseHook,
    HookCallInput,
    DclHookInput,
    BaseDclHook,
    LazyBaseHook,
    Context,
    AnyHookType,
    CompiledHookType,
    LazyImportHook,
)

if TYPE_CHECKING:
    pass


def new_hook_input(context: 'Context', hook_call_dict: dict) -> HookCallInput:
    try:
        hook_input = HookCallInput(**hook_call_dict)
    except ValidationError:
        raise exceptions.HookParseException(
            "", context=context
        )
    return hook_input


def parse_tmp_context(context: 'Context', element: Any, existing_context: dict):
    """
    Parse an arbitrary element. Only used for declarative hook field defaults and in
     the `run_hook` hook in the tackle provider.
    """
    from tackle.parser import walk_document

    tmp_context = new_context()
    tmp_context.key_path = ['->']
    tmp_context.key_path_block = ['->']

    walk_document(context=tmp_context, value=element)

    return tmp_context.public_context


def get_complex_field(field: Any) -> Type:
    """
    Takes an input field such as `list[str]` or `list[SomeOtherHook]` and in the latter
     case will recursively find nested hooks and compile them if needed.
    """
    if isinstance(field, list):
        for i, v in enumerate(field):
            field[i] = get_complex_field(v)
    elif isinstance(field, dict):
        for k, v in field.items():
            field[k] = get_complex_field(v)
    elif isinstance(field, DclHookInput):
        field = field.exec()
    return field


def hook_walk(
        hook: 'BaseHook',
        input_element: Union[list, dict],
        return_: Union[list, dict] = None,
) -> Any:
    """
    Walk an input_element for a function and either return the whole context or one or
     many returnable string keys. Function is meant to be implanted into a function
     object and called either as `exec` or some other arbitrary method.
    """
    if input_element is None:
        # No `exec` method so we'll just be returning the included fields from model
        return hook.model_dump(include=set(hook.hook_input.model_extra.keys()))

    # We have exec data so we need to parse that which will be the return of the hook
    if hook.context.data.public:
        # Move the public data to an existing context
        existing_context = hook.context.data.public.copy()
        # existing_context.update(hook.existing_context)
    else:
        existing_context = {}

    for k, v in hook.hook_input.model_extra.items():
        # Update a function's existing context with the already matched args
        if isinstance(v, dict) and '->' in v:
            # For when the default has a hook in it
            output = parse_tmp_context(
                context=hook.context,
                element={k: v},
                existing_context=existing_context,
            )
            existing_context.update(output)
            try:
                input_element[k] = output[k]
            except KeyError:
                raise exceptions.FunctionCallException(
                    f"Error parsing declarative hook field='{k}'. Must produce an "
                    f"output for the field's default.",
                    function=hook,  # noqa
                ) from None
        else:
            # Otherwise just the value itself
            # existing_context.update({k: get_complex_field(v)})
            existing_context.update({k: getattr(hook, k)})

    hook_context = new_context(
        _hooks=hook.context.hooks,
        existing_data=existing_context,
    )

    from tackle.parser import walk_document

    walk_document(context=hook_context, value=input_element.copy())

    if return_:
        return_ = render_variable(hook_context, return_)
        if isinstance(return_, str):
            if return_ in hook_context.public_context:
                return hook_context.public_context[return_]
            else:
                raise exceptions.FunctionCallException(
                    f"Return value '{return_}' is not found " f"in output.",
                    function=hook,  # noqa
                ) from None
        elif isinstance(return_, list):
            if isinstance(hook_context, list):
                # TODO: This is not implemented (ie list outputs)
                raise exceptions.FunctionCallException(
                    f"Can't have list return {return_} for " f"list output.",
                    function=hook,  # noqa
                ) from None
            output = {}
            for i in return_:
                # Can only return top level keys right now
                if i in hook_context.public_context:
                    output[i] = hook_context.public_context[i]
                else:
                    raise exceptions.FunctionCallException(
                        f"Return value '{i}' in return {return_} not found in output.",
                        function=hook,  # noqa
                    ) from None
            return hook_context.public_context[return_]
        else:
            raise NotImplementedError(f"Return must be of list or string {return_}.")
    return hook_context.data.public


LITERAL_TYPES: set = {'str', 'int', 'float', 'bool', 'dict', 'list'}  # strings to match


def hook_extends_merge_hook(
        context: 'Context',
        func_name: str,
        func_dict: dict,
        extends: str,
):
    base_hook = get_hook(
        context=context,
        hook_type=extends,
        # TODO: this would change if allowing extends to get instantiated with
        #  actual vars. Should be done when allowing dicts for extends.
        args=[],
        kwargs={},
    )
    if base_hook is None:
        raise exceptions.MalformedFunctionFieldException(
            f"In the declarative hook `{func_name}`, the 'extends' reference to "
            f"`{extends}` can not be found.",
            function_name=func_name,
            context=context,
        ) from None
    return {**base_hook().input_raw, **func_dict}


def hook_extends(
        context: 'Context',
        func_name: str,
        func_dict: dict,
):
    """
    Implement the `extends` functionality which takes either a string reference or list
     of string references to declarative hooks whose fields will be merged together.
    """
    extends = func_dict.pop('extends')
    if isinstance(extends, str):
        return hook_extends_merge_hook(
            context=context,
            func_name=func_name,
            func_dict=func_dict,
            extends=extends,
        )

    elif isinstance(extends, list):
        for i in extends:
            if not isinstance(i, str):
                break
            return hook_extends_merge_hook(
                context=context,
                func_name=func_name,
                func_dict=func_dict,
                extends=i,
            )
    raise exceptions.MalformedFunctionFieldException(
        "The field `extends` can only be a string or list of string references to "
        "hooks to merge together.",
        context=context,
        function_name=func_name,
    ) from None


def walk_hook_document(context: 'Context', value: DocumentType):
    from tackle.parser import walk_document
    return walk_document(context=context, value=value)


def get_public_data_from_walk(context: 'Context', value: DocumentType) -> DocumentType:
    walk_hook_document(context=context, value=value)

    return context.data.public


def create_default_factory_walker(
        context: 'Context',
        value: DocumentValueType,
) -> Callable[[], Any]:

    tmp_context = new_context(_hooks=context.hooks)

    return partial(get_public_data_from_walk, tmp_context, value)


def create_validator(
        *,
        context: 'Context',
        value: DocumentValueType,
        field: str,
) -> Callable:
    validator_function = field_validator(field)(
        partial(walk_hook_document, context, value)
    )
    return validator_function

GenericFieldType = typing.TypeVar('GenericFieldType')


def get_hook_field_type(type_str: str) -> GenericFieldType | None:
    from pydantic import networks as pydantic_network_types
    from pydantic import types as pydantic_types
    import ipaddress as ipaddress_types
    import datetime as datetime_types

    if hasattr(typing, type_str):
        return getattr(typing, type_str)
    elif hasattr(ipaddress_types, type_str):
        return getattr(ipaddress_types, type_str)
    elif hasattr(datetime_types, type_str):
        return getattr(datetime_types, type_str)
    elif hasattr(pydantic_types, type_str):
        return getattr(pydantic_types, type_str)
    elif hasattr(pydantic_network_types, type_str):
        return getattr(pydantic_network_types, type_str)


def parse_hook_type(
        context: Context,
        type_str: str,
        hook_name: str,
) -> GenericFieldType:
    """
    Parse the `type` field within a declarative hook and use recursion to parse the
     string into real types.
    """
    if type_str in LITERAL_TYPES:
        # We have a literal type (ie `str`, `list`, `int`, etc)
        # return pydoc.locate(type_str).__name__
        return pydoc.locate(type_str)

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
                type_str=arg,
                hook_name=hook_name,
            )
            for arg in re.split(r',(?![^[\]]*])', type_args_str)
        ]
        # Get base type
        base_type = parse_hook_type(
            context=context,
            type_str=base_type_str,
            hook_name=hook_name,
        )

        if len(type_args) == 0:
            return base_type
        elif base_type == typing.Optional:
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

    # Check if it's a generic type without type arguments
    type_ = get_hook_field_type(type_str=type_str)
    if type_ is not None:
        return type_

    if hasattr(typing, type_str):
        return getattr(typing, type_str)
    elif type_str not in LITERAL_TYPES:
        Hook = get_hooks_from_namespace(context=context, hook_name=type_str)
        if Hook is None:
            try:
                type_ = getattr(typing, type_str.title())
            except AttributeError:
                raise exceptions.MalformedHookFieldException(
                    f"The type `{type_str}` is not recognized. Must be in python's "
                    f"`typing` module, pydantic types, datetime, ipaddress, or a "
                    f"tackle hook.",
                    context=context,
                    hook_name=hook_name,
                ) from None
            return type_
        elif isinstance(Hook, LazyBaseHook):
            # We have a hook we need to build
            raise Exception("Should never happen...")
        else:
            return Hook
    # Treat it as a plain name - Safe to eval as type_str will always be a literal type
    return eval(type_str)


def update_field_dict_with_type(
        *,
        context: 'Context',
        key: str,
        value: DocumentValueType,
        hook_name: str,
        field_dict: dict,
):
    """

    """
    try:
        field_input = FieldInput(**value)
    except ValidationError as e:
        raise exceptions.UnknownInputArgumentException(e, context=context)

    if field_input.enum is not None:
        if field_input.type:
            raise exceptions.MalformedFunctionFieldException(
                'Enums are implicitly typed.',
                context=context,
                function_name=hook_name,
            )
        enum_type = enum.Enum(key, {i: i for i in field_input.enum})
        if field_input.default:
            field_dict[key] = (enum_type, field_input.default)
        else:
            field_dict[key] = (enum_type, ...)
    # elif field_input.type:
    #     if field_input.type in LITERAL_TYPES:
    #         parsed_type = pydoc.locate(field_input.type).__name__
    #     else:
    #         parsed_type = parse_hook_type(
    #             context=context,
    #             type_str=field_input.type,
    #             func_name=hook_name,
    #         )
    #     if field_input.default is not None:
    #         # We have a default and thus need to check
    #         pass
    #     if field_input.description:
    #         field_input.description = field_input.description.__repr__()
    #     field_dict[key] = (
    #         parsed_type,
    #         Field(**value,
    #               default_factory=create_default_factory_walker(
    #                   context=context,
    #                   value=value,
    #               )))
    # elif field_input.default:
    #     if isinstance(field_input.default, dict) and '->' in field_input.default:
    #         # For hooks in the default fields.
    #         field_dict[key] = (Any, Field(**value))
    #     else:
    #         field_dict[key] = (type(field_input.default), Field(**value))
    else:
        if field_input.description:
            field_input.description = field_input.description.__repr__()

        if field_input.parse_keys is None:
            default_factory = None
        elif 'default' in field_input.parse_keys:
            default_factory = create_default_factory_walker(
                context=context,
                value=value['default'],
            )
            # Default is replaced with default factory
            value.pop('default')
        else:
            # TODO: Implement the ability to make additional keys call hooks. Need to
            #  develop use case first though as right now it is not clear unless it is
            #  a default value which
            raise NotImplementedError

        field_dict[key] = (
            parse_hook_type(
                context=context,
                type_str=field_input.type,
                func_name=hook_name,
            ),
            Field(
                **value,
                default_factory=default_factory,
                # This should cause error - dupl instantiation
                # description=field_input.description
            ))
    # else:
    #     field_dict[key] = (dict, value)


def create_dcl_hook_fields(
        context: Context,
        hook_input: DclHookInput,
        hook_name: str,
) -> dict[str, tuple]:
    field_dict: dict[str, tuple] = {}
    for k, v in hook_input.model_extra.items():
        if '<-' in v:
            # Public method
            field_dict[k] = (Callable, LazyBaseHook(input_raw=v, is_public=True))
            continue
        elif '<_' in v:
            # Private method
            field_dict[k] = (Callable, LazyBaseHook(input_raw=v, is_public=False))
            continue
        elif isinstance(v, dict):
            # Dict types are special
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
            field_dict[k] = (v.type_, v.default)
        else:
            raise Exception("This should never happen")

        # function_fields used later to populate functions without an exec method and
        # the context for rendering inputs.
        # field_dict['function_fields'].append(k)
        # hook_input.hook_fields_set_.add(k)
    return field_dict


def new_default_methods() -> dict[str, Callable]:
    pass


DEFAULT_METHODS = new_default_methods()


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
    # Apply overrides to hook_input_raw
    hook_input_dict = update_input_dict(
        input_dict=hook_input_dict,
        update_dict=context.data.overrides,
    )

    # Implement inheritance
    if 'extends' in hook_input_dict and hook_input_dict['extends'] is not None:
        hook_input_dict = hook_extends(
            context=context,
            func_name=hook_name,
            func_dict=hook_input_dict,
        )

    try:
        hook_input = DclHookInput(**hook_input_dict)
    except ValidationError as e:
        raise exceptions.HookParseException(
            f"Invalid input for creating hook=`{hook_name}`. \n {e}",
            context=context
        )

    if hook_input.exec_ is not None and isinstance(hook_input.exec_, dict):
        # Update exec with overrides
        hook_input.exec_ = update_input_dict(
            input_dict=hook_input.exec_,
            update_dict=context.data.overrides,
        )

    # Validators
    if hook_input.validators is not None:
        for k, _ in hook_input.validators.items():
            if k not in hook_input.hook_fields_:
                raise exceptions.UnknownInputArgumentException(
                    f"In the hook definition `{hook_name}`, the field `validators` must be"
                    f" keyed on a field name to apply the validator. Available keys are:"
                    f" {','.join([k for k, _ in hook_input.hook_fields_.items()])}"
                )
            # TODO: give partialmethods on the
            # hook_input.validators[k] = partialmethod(walk_hook_document, context=context)
            setattr(
                hook_input.validators,
                k,
                partialmethod(walk_hook_document, context=context)
            )

    return hook_input


def create_dcl_hook(
        context: 'Context',
        hook_name: str,
        hook_input_raw: dict | str,
) -> 'Type[BaseHook]':
    """Create a model from the function input dict."""
    # Macro to expand all keys properly so that a field's default can be parsed
    hook_input_dict = hook_macros(
        context=context,
        hook_input_raw=hook_input_raw,
        hook_name=hook_name,
    )

    # Serialize known inputs. Implements extends and
    hook_input = new_dcl_hook_input(
        context=context,
        hook_name=hook_name,
        hook_input_dict=hook_input_dict,
    )

    # First pass through the func_dict to parse out the methods
    field_dict = create_dcl_hook_fields(
        context=context,
        hook_input=hook_input,
        hook_name=hook_name,
    )

    # hook_input_types = {k: ( v.annotation, v.default) for k, v in hook_input.__dict__.items()}
    # hook_input_types = {k: v for k, v in hook_input.__dict__.items()}
    # hook_input_types = {k: getattr(BaseDclHook, k) for k, v in hook_input.__dict__.items()}

    # Create a function with the __module__ default to pydantic.main
    try:
        print()
        Hook = create_model(
            hook_name,
            __base__=BaseDclHook,
            # __base__=hook_input,
            __config__=hook_input.hook_model_config_,
            __validators__=hook_input.validators,
            hook_type=(str, hook_name),
            # This is just to preserve the inputs - consider removing
            hook_input=(HookCallInput, hook_input),
            # **hook_input.__dict__,
            help=(str, hook_input.help),
            args=(list, hook_input.args),
            **field_dict,
        )
    except NameError as e:
        if 'shadows a BaseModel attribute' in e.args[0]:
            shadowed_arg = e.args[0].split('\"')[1]
            extra = "a different value"
            raise exceptions.ShadowedHookFieldException(
                f"The function field \'{shadowed_arg}\' is reserved. Use {extra}.",
                function_name=hook_name,
                context=context,
            ) from None
        # Don't know what else could happen
        raise e
    except Exception as e:
        raise e

    # Create an 'exec' method on the function that can be called later.
    setattr(
        Hook,
        'exec',
        partialmethod(hook_walk, hook_input.exec_, hook_input.return_),
    )

    # TODO: Rm when filters fixed
    # context.env_.filters[func_name] = Function(
    #     existing_context={},
    #     no_input=context.no_input,
    # ).wrapped_exec

    return Hook


def create_dcl_method(
        context: 'Context',
        hook: AnyHookType,
        arg: str,
):
    method = hook.model_fields[arg].default
    # Update method with values from base class so that fields can be inherited
    # from the base hook. function_fields is a list of those fields that aren't
    # methods / special vars (ie args, return, etc).
    for i in hook.model_fields['function_fields'].default:
        # Base method should not override child.
        if i not in method.input_raw:
            method.input_raw[i] = hook.model_fields['function_dict'].default[i]
            if method.hook_fields is None:
                method.hook_fields = []
            method.hook_fields.append(i)

    return create_dcl_hook(
        context=context,
        hook_name=arg,
        hook_input_raw=method.input_raw.copy(),
    )


def enrich_hook(
        context: 'Context',
        Hook: CompiledHookType,
        args: list,
        kwargs: dict,
        hook_type: str = None,
) -> CompiledHookType:
    """
    Take a hook and enrich it by lining up the args with potential methods / hook args /
     kwargs. For methods, it recognizes the arg is a method, compiles the method hook
     with the attributes of the base hook making it inherit them.
    """
    # Handle args
    for n, arg in enumerate(args):
        # If help and last arg
        if arg == 'help' and n == len(args):
            # This should be handled upstream right?
            # run_help(context, Hook)
            raise
        # When arg inputs are not hashable then they are actual arguments which will be
        # consumed later
        elif isinstance(arg, (list, dict)):
            # TODO: Check how this logic works with `args` condition below which works
            #  for bypassing the processing of args for later logic
            pass
        # If arg in methods, compile hook
        elif arg in Hook.model_fields and Hook.model_fields[arg].annotation == Callable:
            Hook = create_dcl_method(
                context=context,
                hook=Hook,
                arg=args.pop(0)
            )
            if len(args) != 0:
                return enrich_hook(
                    context=context,
                    Hook=Hook,
                    args=args,
                    kwargs=kwargs,
                    hook_type=arg,
                )
        elif 'args' in Hook.model_fields:
            # The hook takes positional args
            pass
        else:
            raise exceptions.UnknownInputArgumentException(
                f"Unknown arg supplied `{arg}`",
                context=context,
            )
    return Hook


def upgrade_lazy_hook(
        context: Context,
        hook_type: str,
        Hook: AnyHookType | None,
) -> CompiledHookType | None:
    """
    Upgrade lazy hooks to compiled hooks.

    TODO: Describe what these are
    TODO: Hook should be reinserted into hooks so as to avoid duplicate compilation?
        This is a question as we need to verify using a hook twice doesn't store data
        in the instantiated hook. Would need to make a copy of the hook potentially
    """
    if Hook is None:
        return Hook
    # This gets hit when you use an imported declarative hook
    if isinstance(Hook, LazyBaseHook):
        Hook = create_dcl_hook(
            context=context,
            hook_name=hook_type,
            hook_input_raw=Hook.input_raw.copy(),
        )
        # TODO: See if there is any issue reinserting this into the appropriate hook
        #  access group. Issue is access groups
    elif isinstance(Hook, LazyImportHook):
        import_with_fallback_install(
            context=context,
            provider_name=Hook.mod_name,
            hooks_directory=Hook.hooks_path,
        )
        Hook = get_public_or_private_hook(
            context=context,
            hook_type=Hook.hook_type,
        )
        # Reinserting upgraded hook back in appropriate hook access group
        #  TODO: Test this
        # if Hook.is_public:
        #     context.hooks.public[hook_type] = Hook
        # else:
        #     context.hooks.private[hook_type] = Hook

    return Hook


def get_public_or_private_hook(
        context: 'Context',
        hook_type: str,
) -> CompiledHookType | None:
    """Get the public or private hook from the context."""
    Hook = context.hooks.public.get(hook_type, None)
    if Hook is not None:
        return upgrade_lazy_hook(
            context=context,
            hook_type=hook_type,
            Hook=Hook,
        )
    Hook = context.hooks.private.get(hook_type, None)
    if Hook is not None:
        return upgrade_lazy_hook(
            context=context,
            hook_type=hook_type,
            Hook=Hook,
        )
    return None  # Caught later


def get_hook(
        context: 'Context',
        hook_type: str,
        args: list,
        kwargs: dict,
) -> Optional[CompiledHookType]:
    """Gets the hook from the context and calls enrich_hook."""
    hook = get_public_or_private_hook(context=context, hook_type=hook_type)
    if hook is None:
        return None
    return enrich_hook(
        context=context,
        Hook=hook,
        args=args,
        kwargs=kwargs,
        hook_type=hook_type,
    )
