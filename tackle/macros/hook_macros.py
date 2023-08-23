"""
Declarative hook macros. Handles all the inputs to hooks (ie `hook_name<-`). Removes
any arrows from keys based on if they are hook calls or methods.
"""
from typing import TYPE_CHECKING

from tackle import exceptions

from tackle.models import DclHookInput

if TYPE_CHECKING:
    from tackle.models import Context

FUNCTION_ARGS = {
    DclHookInput.model_fields[i].alias
    if DclHookInput.model_fields[i].alias is not None else
    i for i in DclHookInput.model_fields.keys()
}


def dict_hook_method_macros():
    pass


from tackle.methods import new_default_methods

DEFAULT_METHODS = new_default_methods()
LITERAL_TYPES = {'str', 'list'}


def dict_hook_macro(context: 'Context', hook_input_raw: dict) -> dict:
    """Remove any arrows from keys."""
    new_hook_input = {}
    # Special case where we don't need an arrow
    if 'exec' in hook_input_raw:
        new_hook_input['exec<-'] = hook_input_raw.pop('exec')

    for k, v in hook_input_raw.items():
        if k.endswith(('<-', '<_')):
            # We have a method. Value handled elsewhere
            new_hook_input[k[-2:]] = {k[-2:]: v}
        elif k.endswith(('->', '_>')):
            if not isinstance(v, str):
                raise exceptions.UnknownInputArgumentException(
                    f"Hook definition fields ending with arrow (ie `{k}`) must have"
                    f" string values.", context=context
                )
            arrow = k[-2:]
            # exclude = True if arrow == '_>' else False
            new_hook_input[k[:-2]] = {
                'default': v,
                'exclude': True if arrow == '_>' else False,
                'parse_keys': ['default']
            }
        elif v is None:
            new_hook_input[k] = {'type': 'Any', 'default': None}
        elif isinstance(v, str) and v in LITERAL_TYPES:
            new_hook_input[k] = {'type': v}
        elif isinstance(v, dict):
            # dict inputs need to be checked for keys with an arrow (ie default->)
            # TODO: Traverse and apply logic

            new_hook_input[k] = v
        else:
            # Otherwise just put as default value with same type
            new_hook_input[k] = {'type': type(v).__name__, 'default': v}

    return new_hook_input


def str_hook_macro(hook_input_raw: str) -> dict:
    """
    String hook macro converts to a dict that executes and returns the key as a hook.
    From: foo<-: literal bar
    To: foo<-:
          tmp_in->: literal bar
          tmp_out->: return {{tmp_in}}
    """
    return {'tmp_in->': hook_input_raw, 'tmp_out->': 'return {{tmp_in}}'}


def hook_macros(context: 'Context', hook_input_raw: dict | str) -> dict:
    """
    Macro to update the keys of a declarative hook definition and parse out any methods.
    """

    if isinstance(hook_input_raw, str):
        return str_hook_macro(hook_input_raw=hook_input_raw)
    elif isinstance(hook_input_raw, dict):
        return dict_hook_macro(context=context, hook_input_raw=hook_input_raw)
    else:
        raise Exception("This should never happen...")
