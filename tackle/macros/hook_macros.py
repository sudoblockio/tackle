"""
Declarative hook macros. Handles all the inputs to hooks (ie `hook_name<-`). Removes
any arrows from keys based on if they are hook calls or methods.
"""
from pydantic.fields import FieldInfo
from ruyaml.constructor import CommentedMap, CommentedSeq, ScalarFloat

from tackle import Context, exceptions
from tackle.macros.function_macros import function_macro
from tackle.models import DCL_HOOK_FIELDS

LITERAL_TYPES = {'list', 'dict', 'str', 'int', 'float', 'bytes', 'bool'}

DEFAULT_FACTORY_KEYS = [
    'default->',
    'default_>',
    'default_factory->',
    'default_factory_>',
    '->',
    '_>',
]


def update_default_factory_hook_fields(
    context: Context,
    hook_name: str,
    value: dict,
):
    """
    Any `default` or `default_factory` key ending in an arrow will be transformed into
     a `default_factory` field with the arrow indicating if the field is excluded or
     included based on the access modifier (-> vs _>) of the arrow. Reasoning is arrows
     indicate parsables so an arrow ending in an arrow must be a default_factory field
     which is callable so this function is sort pre-process before that callable is
     assembled.

    Examples:
     public / included `->` or private / excluded `_>`.
     default_>: {...} => default_factory: {excluded: True, ...}
    """
    for key in DEFAULT_FACTORY_KEYS:
        if key in value:
            if 'default_factory' in value:
                raise exceptions.MalformedHookFieldException(
                    f"Cannot have both '{key}' and 'default_factory' in hook field.",
                    context=context,
                    hook_name=hook_name,
                )
            if len(key) == 2:
                value = {'default_factory': value}
            else:
                value['default_factory'] = {key[-2:]: value.pop(key)}
            if key[-2:] == '_>':
                value['exclude'] = True
            return value
    # # TODO:
    # if isinstance(value, dict):
    #     if 'default' in value:
    #         if isinstance(value['default'], (list, dict)):
    #             value['default_factory'] = value.pop('default')
    #             return value

    return value


def expand_default_factory(
    value: dict,
    key: str,
):
    """
    Expand keys for special cases where we have string values or bare arrows as a key
     which both indicate hook calls. Ignores anything that doesn't have a
     `default_factory` field which this acts on.
    """
    if 'default_factory' not in value:
        return
    elif value['default_factory'] is None:
        value['default_factory'] = {
            f'{key}->': value['default_factory'],
            'return->': key,
        }
    elif isinstance(value['default_factory'], str):
        # Convert to dict which then returns the key
        value['default_factory'] = {
            f'{key}->': value['default_factory'],
            'return->': key,
        }
    elif '->' in value['default_factory'] or '_>' in value['default_factory']:
        # Already have whole arrow so nest value in a key and return that
        value['default_factory'] = {
            key: value['default_factory'],
            'return->': key,
        }


def infer_type_from_default(value: dict):
    """When a `default` field exists but not a `type` we infer the type."""
    if 'enum' in value:
        # enum fields don't get a type by default
        return
    if 'default' in value and 'type' not in value:
        # Has default field but not a type so assuming the type is the default.
        default = value['default']
        # ruyaml uses its own types so need special logic for them
        if isinstance(default, (CommentedMap, dict)):
            if '->' in default or '_>' in default:
                value['type'] = 'Any'
            else:
                value['type'] = 'dict'
        elif isinstance(default, ScalarFloat):
            value['type'] = 'float'
        elif isinstance(default, CommentedSeq):
            value['type'] = 'list'
        else:
            value['type'] = type(value['default']).__name__
        return value
    elif 'default_factory' in value and 'type' not in value:
        # Don't know type so just assume Any as output of default factory
        value['type'] = 'Any'


# Any of these fields and the value is a field
MINIMAL_FIELD_KEYS = [
    'type',
    'default',
    'default_factory',
    'enum',
]


def is_field(value: dict) -> bool:
    """
    Determines if a value is a pydantic field or if it is just a dict. Some minimal
     fields are required for it to be a field.
    """
    for i in MINIMAL_FIELD_KEYS:
        if i in value:
            return True
    return False


def dict_field_hook_macro(
    context: Context,
    hook_name: str,
    key: str,
    value: dict,
) -> dict:
    """
    Transform dict values so that they are parseable by creating a callable as a
     default factory that includes the dict. This will be called unless a value is
     given. Handles cases when a type is not given which it then assumes as `Any` since
     it is not known. Handles a lot of edge cases such as:

     field->: a_hook args
     field: {->: a_hook, key: value}
     field: {default->: a_hook args}
     field: {random_key: {->: a_hook args}}

    In all these cases it is expanded to:

    field:
      type: Any  # Only if `type` does not exist
      default_factory:
        field->: a_hook args
        return->: {{field}}
    """
    # Transform fields ending in a hook call to a field with a default factory
    value = update_default_factory_hook_fields(context, hook_name, value=value)

    # Expand any default_factory fields - value = str or dict with arrow
    expand_default_factory(value=value, key=key)

    # When a `default` field exists but not a `type` field we infer the `type`
    infer_type_from_default(value=value)

    # Check minimal fields to see if we can just return the value as a default factory
    if not is_field(value):
        # Just make dict values parseable
        return {'default_factory': value, 'type': 'Any'}

    # Make the default_factory callable
    return value


def hook_dict_macro(
    context: 'Context',
    hook_input_raw: dict,
    hook_name: str,
) -> dict:
    """Remove any arrows from keys."""
    output = {}
    # Special case where we don't need an arrow which can often be forgotten
    # TODO: `exec` method arrow meaning will change
    if 'exec<-' in hook_input_raw:
        output['exec'] = hook_input_raw.pop('exec<-')

    if 'exec<_' in hook_input_raw:
        raise exceptions.MalformedHookFieldException(
            "Right now we don't support private exec methods. See 'Private `exec`"
            " Method proposal",
            context=context,
            hook_name=hook_name,
        )

    for k, v in hook_input_raw.items():
        if k in DCL_HOOK_FIELDS:
            # Don't run a macro on any field that is part of base
            output[k] = v
        elif k.endswith(('<-', '<_')):
            # A method
            hook_name, hook_value, methods = function_macro(context, k[:-2], value=v)
            if methods:  # Can't define functional macros yet
                raise NotImplementedError("Haven't implemented functional methods yet.")
            output[hook_name] = {k[-2:]: hook_value}
        elif k.endswith(('->', '_>')):
            output[k[:-2]] = dict_field_hook_macro(
                context=context,
                hook_name=hook_name,
                key=k[:-2],
                value={f'default_factory{k[-2:]}': v},
            )
        elif v is None:
            output[k] = {'type': 'Any', 'default': None}
        elif isinstance(v, str) and v in LITERAL_TYPES:
            output[k] = {'type': v}
        elif isinstance(v, dict):
            output[k] = dict_field_hook_macro(
                context=context,
                hook_name=hook_name,
                key=k,
                value=v,
            )
        elif isinstance(v, list):
            output[k] = {'type': 'list', 'default_factory': v}
        elif isinstance(v, FieldInfo):
            output[k] = v
        else:
            # Otherwise just put as default value with same type
            output[k] = {'type': type(v).__name__, 'default': v}
    return output


def str_hook_macro(hook_input_raw: str) -> dict:
    """
    String hook macro converts to a dict that executes and returns the key as a hook.
    From: foo<-: literal bar
    To: foo<-:
          tmp_in->: literal bar
          tmp_out->: return {{tmp_in}}
    """
    return {'tmp_in->': hook_input_raw, 'tmp_out->': 'return tmp_in'}


def hook_macros(
    context: 'Context',
    hook_input_raw: dict | str,
    hook_name: str,
) -> dict:
    """
    Macros used when creating declarative hooks mostly focused on transforming fields
     so that they can be properly serialized.
    """
    if isinstance(hook_input_raw, str):
        value = str_hook_macro(hook_input_raw=hook_input_raw)
        return hook_dict_macro(
            context=context,
            hook_input_raw=value,
            hook_name=hook_name,
        )
    elif isinstance(hook_input_raw, dict):
        return hook_dict_macro(
            context=context,
            hook_input_raw=hook_input_raw,
            hook_name=hook_name,
        )
    else:
        raise Exception("This should never happen...")
