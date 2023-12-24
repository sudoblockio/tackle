import ast
import re
from typing import Any, Dict

from tackle import Context, exceptions
from tackle.types import DEFAULT_HOOK_NAME, DocumentValueType


def split_on_outer_parentheses(text):
    """Split up a string based on balanced outermost parentheses."""
    # Pattern to match balanced outermost parentheses (including nested) or
    # non-parenthesis text
    pattern = r'\([^()]*\)|\((?:[^()]|\([^()]*\))*\)'
    matches = re.findall(pattern, text)

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

    return split_segments


def eval_quoted_string(s):
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
    - Split on commas that are not encapsulated by brackets
    - Iterate over split items - these are the args
    - Split on equal sign
    - If len is 1 - First item is the type
        - Cleanup types based on if the item is quoted or not and eval as literal
    - If len is 2 - Second item is the default
    """
    # Once we have found a kwarg we don't accept positional non-default args and throw
    found_kwarg = False
    output = {}
    arg_name_list = []
    split_func_args = re.split(r',\s*(?![^\[\]{}()]*[\]\}])', func_str)
    for arg in split_func_args:
        arg_split = re.split(r' ', arg, maxsplit=1)
        arg_name = arg_split.pop(0)
        if arg_name == '':
            # Empty function signature
            break
        output[arg_name] = {}
        if len(arg_split) == 0:
            output[arg_name]['type'] = 'Any'
            raise_if_found_arg(context, found_kwarg, key_raw)
            continue
        arg_default_split = arg_split[0].split('=')
        output[arg_name]['type'] = arg_default_split.pop(0).strip()
        if not arg_default_split:
            # No default means it is a positional arg
            raise_if_found_arg(context, found_kwarg, key_raw)
            arg_name_list.append(arg_name)
        elif len(arg_default_split) == 1:
            output[arg_name]['default'] = eval_quoted_string(arg_default_split[0])
            found_kwarg = True
        else:
            raise exceptions.MalformedHookDefinitionException(
                "",
                context=context,
                hook_name=key_raw,
            )

    output['args'] = arg_name_list
    output['exec'] = value
    return output


def parse_method_receiver(
    context: Context,
    hook_split: list[str],
    value: Any,
    key_raw: str,
) -> Dict[str, Any]:
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
     parenthesis wrapped function signature expression. For instance:

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

    Similarly

    Process:
    - Split the string on outer parenthesis
        - Extract the function name
    - Split on commas that are not encapsulated by brackets
    - Iterate over chars until getting to whitespace - this is the variable name
    - Iterate over chars until getting to equal sign - this is the variable type
    - If hit equal sign, the remaining items are the default
    """
    hook_split = split_on_outer_parentheses(key_raw)
    match len(hook_split):
        case 0:
            return DEFAULT_HOOK_NAME, value, None
        case 1:
            # Hook
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