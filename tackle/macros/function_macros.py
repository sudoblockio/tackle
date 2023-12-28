"""
Examples:

foo(bar str, baz str | int, bin union[base, str] = 'stuff') ->: old_value

Should expand to:

hook_name: foo
value:
  bar:
    type: str
  baz:
    type: str | int
  bin:
    type: union[base, str]
    default: stuff
  exec: old_value

Similarly, for methods:

(f foo) bar (baz str) ->: old_value

Should expand to:

hook_name: foo
self_name: f
method_name: bar
method_fields:
  bar:
    type: str
  baz:
    type: str | int
  bin:
    type: union[base, str]
    default: stuff
  exec: old_value
"""
import ast
import logging
import re
from typing import Any, Dict

from tackle import Context, exceptions
from tackle.models import BaseHook
from tackle.types import DEFAULT_HOOK_NAME, DocumentValueType

logger = logging.getLogger(__name__)


def split_on_outer_parentheses(text: str) -> (bool, list):
    """
    Splits a string based on balanced, outermost parentheses.

    This function identifies segments enclosed by top-level parentheses and segments
     outside any parentheses. It handles nested parentheses as well. Returns tuple with
     a boolean to know if we did split or a non-enclosed parenthesis.
    """
    # Pattern to match balanced outermost parentheses (including nested) or
    # non-parenthesis text
    matches = re.findall(r'\([^()]*\)|\((?:[^()]|\([^()]*\))*\)', text)

    # Split the text by these matches and include the matches
    split_segments = []
    last_end = 0
    for match in matches:
        start, end = re.search(re.escape(match), text).span()
        # Add segment before the match, if it's not empty
        if start > last_end:
            split_segments.append(text[last_end:start])
        # Add the matched segment without outermost parentheses
        split_segments.append(match[1:-1])
        last_end = end

    # Add remaining part of the text after the last match
    if last_end < len(text):
        split_segments.append(text[last_end:])

    # Since the default hook has no func name, we need to disambiguate that in return
    if len(matches) == 0:
        did_split = False
    else:
        did_split = True

    return did_split, split_segments


def eval_quoted_string(s: str):
    """
    Evaluates a quoted string as a Python literal if possible.

    If the string is enclosed in single or double quotes, it removes the quotes
    and attempts to evaluate the string as a Python literal using `ast.literal_eval`.
    If the evaluation fails, it returns the original string without quotes.
    """
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        # Remove the quotes
        s = s[1:-1]
    try:
        # Safely evaluate the string to a Python literal
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        # Return the original string if it cannot be evaluated to a literal
        return s.strip()


def raise_if_found_arg(context: Context, found_kwarg: bool, key_raw: str):
    """Raise an exception if a positional argument is found after a keyword argument."""
    if found_kwarg:
        raise exceptions.MalformedHookDefinitionException(
            "Can't put positional arguments before key word arguments in the "
            f"hook definition `{key_raw}`",
            context=context,
            hook_name=key_raw,
        )


def parse_function_args(
    context: Context,
    func_str: str,
    value: Any,
    key_raw: str,
) -> dict:
    """
    Parses function arguments from a string representation.

    This function processes a string containing function arguments, splitting them
     into individual arguments and extracting their types and default values.
    """
    # Once we have found a kwarg we don't accept positional non-default args and throw
    found_kwarg = False
    output = {}
    arg_name_list = []
    split_func_args = re.split(r',\s*(?![^\[\]{}()]*[\]\}])', func_str)
    for arg in split_func_args:
        default_split = re.split(r'=', arg, maxsplit=1)
        if len(default_split) == 2:
            default = eval_quoted_string(default_split.pop(1))
        else:
            default = None

        type_split = re.split(r' ', default_split[0], maxsplit=1)
        if len(type_split) == 2:
            type_ = type_split.pop(1).strip()
        else:
            type_ = 'Any'

        arg_name = type_split[0]
        if arg_name == '':
            # Empty function signature
            break

        if arg_name in BaseHook.model_fields:
            if type_ != 'Any':
                logger.debug(
                    f"In the function def=`{key_raw}`, the field=`{arg_name}` is "
                    f"reserved and should not specify a type=`{type_}`"
                )
            output[arg_name] = default
            continue

        arg_name_list.append(arg_name)
        output[arg_name] = {'type': type_}
        if not default:
            # No default means it is a positional arg
            raise_if_found_arg(context, found_kwarg, key_raw)
        else:
            output[arg_name]['default'] = default
            found_kwarg = True

    output['args'] = arg_name_list
    output['exec'] = value
    return output


def parse_method_receiver(
    context: Context,
    hook_split: list[str],
    value: Any,
    key_raw: str,
) -> Dict[str, Any]:
    """Parses a method receiver from a split hook string."""
    output = {
        'method_name': hook_split[1],
        'method_fields': parse_function_args(
            context,
            func_str=hook_split[2],
            value=value,
            key_raw=key_raw,
        ),
    }
    method_split = hook_split[0].split(' ')
    match len(method_split):
        case 1:
            output['self_name'] = None  # noqa
            output['hook_name'] = method_split[0]
        case 2:
            output['self_name'] = method_split[0]
            output['hook_name'] = method_split[1]
        case _:
            raise exceptions.MalformedHookDefinitionException(
                "",
                context=context,
                hook_name=key_raw,
            )
    return output


def function_macro(
    context: Context,
    key_raw: str,
    value: DocumentValueType,
) -> (str, DocumentValueType, dict[str, dict[str, Any]]):  # hook_name, value, methods
    """
    Macro to expand declarative hook keys into functions if they contain a string with a
     parenthesis wrapped function signature expression.

    Routes the parsing for functions and methods based on splitting the input string key
     on closing parenthesis.
    """
    did_split, hook_split = split_on_outer_parentheses(key_raw)
    match len(hook_split):
        case 0:
            return DEFAULT_HOOK_NAME, value, None
        case 1:
            # Hook - either default or normal hook
            if did_split:
                return (
                    DEFAULT_HOOK_NAME,
                    parse_function_args(context, hook_split[0], value, key_raw),
                    None,
                )
            return hook_split[0], value, None
        case 2:
            # Function
            return (
                hook_split[0],
                parse_function_args(context, hook_split[1], value, key_raw),
                None,
            )
        case 3:
            # Method
            return (
                None,
                None,
                parse_method_receiver(context, hook_split, value, key_raw),
            )
        case _:
            raise exceptions.MalformedHookDefinitionException(
                "Detected more than two sets of enclosed parenthesis. Should be at "
                "most 2, leading set for methods and trailing set for functions.",
                context=context,
                hook_name=key_raw,
            )
