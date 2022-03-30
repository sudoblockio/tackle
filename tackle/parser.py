import os
import re
import logging
import warnings
from pathlib import Path
from functools import partialmethod
from typing import Type, Any, Union
from pydantic import Field, create_model
from pydantic.main import ModelMetaclass

from tackle.render import render_variable, wrap_jinja_braces
from tackle.utils.dicts import (
    nested_get,
    nested_delete,
    nested_set,
    encode_list_index,
    set_key,
    get_readable_key_path,
)
from tackle.utils.command import unpack_args_kwargs_string
from tackle.utils.vcs import get_repo_source
from tackle.utils.files import read_config_file
from tackle.utils.paths import (
    work_in,
    is_repo_url,
    is_directory_with_tackle,
    is_file,
    find_tackle_file,
    find_nearest_tackle_file,
    find_in_parent,
)
from tackle.utils.zipfile import unzip
from tackle.models import Context, BaseHook, LazyImportHook, BaseFunction, FunctionInput
from tackle.exceptions import (
    HookCallException,
    UnknownHookTypeException,
    UnknownArgumentException,
    UnknownSourceException,
    EmptyTackleFileException,
    EmptyBlockException,
)
from tackle.settings import settings

logger = logging.getLogger(__name__)


def get_hook(hook_type, context: 'Context'):
    """
    Get the hook from available providers and install hook requirements if they haven't
    been already.

    This function does the following to return the hook:
    1. Check if hook hasn't been imported already
    2. Check if the hook has been declared in a provider's __init__.py's
    `hook_types` field.
    3. Try to import it then fall back on installing the requirements.txt file
    """
    h = context.provider_hooks.get(hook_type, None)
    if h is None:
        # Show this without verbose:
        available_hooks = (
            "Run the application with `--verbose` to see available hook types."
        )
        if context.verbose:
            available_hooks = 'Available hooks = ' + ' '.join(
                [str(i) for i in context.provider_hooks.keys()]
            )
        raise UnknownHookTypeException(
            f"The hook type=\"{hook_type}\" is not available in the providers. "
            + available_hooks
        )

    # LazyImportHook in hook ref when declared in provider __init__.hook_types
    if isinstance(h, LazyImportHook):
        # Install the requirements which will convert all the provider
        context.provider_hooks.import_with_fallback_install(
            mod_name=h.mod_name,
            path=h.hooks_path,
        )
        h = context.provider_hooks[hook_type]
    return h


def evaluate_for(hook_dict: dict, Hook: ModelMetaclass, context: 'Context'):
    """Run the parse_hook function in a loop and return a list of outputs."""
    loop_targets = render_variable(context, wrap_jinja_braces(hook_dict['for']))
    hook_dict.pop('for')

    # Need add an empty list in the value so we have something to append to
    set_key(
        element=context.output_dict,
        keys=context.key_path,
        value=[],
    )

    if len(loop_targets) == 0:
        return

    for i, l in (
        enumerate(loop_targets)
        if not render_variable(context, hook_dict.get('reverse', None))
        else reversed(list(enumerate(loop_targets)))
    ):
        # Create temporary variables in the context to be used in the loop.
        context.existing_context.update({'index': i, 'item': l})
        # Append the index to the keypath
        context.key_path.append(encode_list_index(i))

        # TODO: Do we need to parse a copy of the hook?
        parse_hook(hook_dict.copy(), Hook, context, append_hook_value=True)
        context.key_path.pop()

    # Remove temp variables
    context.existing_context.pop('item')
    context.existing_context.pop('index')


def evaluate_if(hook_dict: dict, context: 'Context', append_hook_value: bool) -> bool:
    """Evaluate the if/when condition and return bool."""
    if hook_dict.get('when', None) is not None:
        result = render_variable(context, wrap_jinja_braces(hook_dict['when']))
        hook_dict.pop('when')
        return result
    if hook_dict.get('for', None) is not None and not append_hook_value:
        # We qualify `if` conditions within for loop logic
        return True
    if hook_dict.get('if', None) is None:
        return True

    return render_variable(context, wrap_jinja_braces(hook_dict['if']))


def merge_block_output(
    hook_output_value: Any,
    key_path: list,
    output_dict: dict,
    append_hook_value: bool = False,
):
    """
    Block hooks have already written to the output dict so to merge, need to take the
     keys from the key path and move them up one level.
    """
    if append_hook_value:
        raise HookCallException("Can't merge from for loop.")

    indexed_block_output = nested_get(element=hook_output_value, keys=key_path)
    for k, v in indexed_block_output.items():
        nested_set(
            element=output_dict,
            keys=[k] + key_path[:-1],
            value=v,
        )
    nested_delete(element=output_dict, keys=key_path)


def merge_output(
    hook_output_value: Any,
    key_path: list,
    output_dict: dict,
    append_hook_value: bool = False,
):
    """Merge the contents into it's top level set of keys."""
    if append_hook_value:
        raise HookCallException("Can't merge from for loop.")

    if key_path[-1] in ('->', '_>'):
        # Expanded key - Remove parent key from key path
        key_path = key_path[:-2] + [key_path[-1]]
    else:
        # Compact key
        key_path = key_path[:-1] + [key_path[-1][-2:]]

    # Can't merge into top level keys without merging k/v individually
    if len(key_path) == 1:
        # This is only valid for dict output
        if isinstance(hook_output_value, dict):
            for k, v in hook_output_value.items():
                set_key(
                    element=output_dict,
                    keys=[k] + key_path,
                    value=v,
                )
            return
        else:
            raise HookCallException("Can't merge non maps into top level keys.")
    else:
        set_key(
            element=output_dict,
            keys=key_path,
            value=hook_output_value,
        )


def run_hook_in_dir(hook: Type[BaseHook]) -> Any:
    if hook.chdir:
        path = os.path.abspath(os.path.expanduser(hook.chdir))
        if os.path.isdir(path):
            # Use contextlib to switch dirs
            with work_in(os.path.abspath(os.path.expanduser(hook.chdir))):
                return hook.exec()
        else:
            raise NotADirectoryError(
                f"The specified path='{path}' to change to was not found."
            )
    else:
        return hook.exec()


def run_hook_with_try(hook: Type[BaseHook]) -> Any:
    """Handle changing dir attribute."""
    if hook.try_:
        try:
            return run_hook_in_dir(hook)
        except Exception:
            return
    else:
        # Normal hook run
        return run_hook_in_dir(hook)


def render_hook_vars(hook_dict: dict, Hook: ModelMetaclass, context: 'Context'):
    """Render the hook variables."""
    for key, value in list(hook_dict.items()):
        if key in Hook.Config.alias_to_fields:
            # Skip any keys used in logic as these are evaluated / rendered separately
            continue

        if key in Hook._render_exclude or key in Hook._render_exclude_default:
            # Skip anything that has been marked excluded. Needed for things like block
            # hooks which will have templating within the inputs
            continue

        if isinstance(value, str):
            # Check Hook private vars for rendering by default which wraps bare strings
            if key in Hook._render_by_default:
                hook_dict[key] = render_variable(context, wrap_jinja_braces(value))

            # TODO: When we build our own custom Field function then this will change
            elif 'render_by_default' in Hook.__fields__[key].field_info.extra:
                hook_dict[key] = render_variable(context, wrap_jinja_braces(value))

            elif '{{' in value and '}}' in value:
                hook_dict[key] = render_variable(context, value)

        elif isinstance(value, (list, dict)):
            hook_dict[key] = render_variable(context, value)


def parse_hook(
    hook_dict, Hook: ModelMetaclass, context: 'Context', append_hook_value: bool = None
):
    """Parse input dict for loop and when logic and calls hooks."""
    if evaluate_if(hook_dict, context, append_hook_value):

        if 'for' in hook_dict:
            # This runs the current function in a loop with `append_hook_value` set so
            # that keys are appended in the loop.
            evaluate_for(hook_dict, Hook, context)
            return

        else:
            # Render the remaining hook variables
            render_hook_vars(hook_dict, Hook, context)

            hook = Hook(
                **hook_dict,
                input_dict=context.input_dict,
                output_dict=context.output_dict,
                existing_context=context.existing_context,
                no_input=context.no_input,
                calling_directory=context.calling_directory,
                calling_file=context.calling_file,
                provider_hooks=context.provider_hooks,
                key_path=context.key_path,
                verbose=context.verbose,
                env_=context.env_,
                is_hook_call=True,
            )
            # Main exec logic
            hook_output_value = run_hook_with_try(hook)

            if hook.hook_type == 'block':
                if hook.merge:
                    merge_block_output(
                        hook_output_value=hook_output_value,
                        key_path=context.key_path,
                        output_dict=context.output_dict,
                        append_hook_value=append_hook_value,
                    )
                return
            elif hook.merge:
                merge_output(
                    hook_output_value=hook_output_value,
                    key_path=context.key_path,
                    output_dict=context.output_dict,
                    append_hook_value=append_hook_value,
                )
            else:
                set_key(
                    element=context.output_dict,
                    keys=context.key_path,
                    # keys=context.key_path[-len(context.key_path_block):],
                    value=hook_output_value,
                    append_hook_value=append_hook_value,
                )

    elif 'else' in hook_dict:
        if isinstance(hook_dict['else'], str):
            set_key(
                element=context.output_dict,
                keys=context.key_path,
                # keys=context.key_path[:-len(context.key_path_block)],
                value=render_variable(context, hook_dict['else']),
                append_hook_value=append_hook_value,
            )
            return
        context.key_path.pop()  # Remove the prior hook call
        walk_sync(context, element=hook_dict['else'])
        context.key_path.append('hack')  #
    elif 'else->' in hook_dict:
        if isinstance(hook_dict['else->'], str):
            context.key_path[-1] = '->'
            # Issue is we need to maintain a consistent render context during exec
            raise NotImplementedError("Compact else not implemented.")
        raise NotImplementedError("Compact else not implemented.")

    # TODO: Ultra hack - Should be RMed -
    elif context.key_path[-1] in ('->', '_>'):
        if hook_dict['hook_type'] == 'block':
            context.key_path.pop()


def evaluate_args(args: list, hook_dict: dict, Hook: Type[BaseHook]):
    """
    Associate hook arguments provided in the call with hook attributes. Parses the
    hook's `_args` attribute to know how to map arguments are mapped to where and
    deal with rendering by default.

    TODO: This needs to be re-thought. Right now we parse the inputs without regard
     for the types of the argument mapping. What could be better is if we know the types
     of the arg mapping ahead of time and they try to assemble the most logical mapping
     afterwards. So if the mapping consists of a [str, list], then the if the first
     args are strs then we can ignore the list part. Right now it would just join all
     the strings together if they are part of last arg mapping.

    Solutions:
    - First try to infer type from arg
        - Single types then into unions?
    - If type cannot be infered (ie Any) then do ast as literal
    """

    hook_args: list = Hook.__fields__['args'].default
    for i, v in enumerate(args):
        # Iterate over the input args
        if i + 1 == len(hook_args):
            # We are at the last argument mapping so we need to join the remaining
            # arguments as a single string if it is not a list of another map.
            if not isinstance(args[i], (str, float)):
                # Catch list dict and ints - strings floats and bytes caught later
                value = args[i]
            elif Hook.__fields__[hook_args[i]].type_ in (str, float, int):
                # Was parsed on spaces so reconstructed.
                value = ' '.join(args[i:])
            # fmt: skip
            elif isinstance(Hook.__fields__[hook_args[i]], list):
                # If list then all the remaining items
                value = args[i:]
            elif isinstance(v, (str, float, int)):
                # Make assumption the rest of the args can be reconstructed as above
                value = ' '.join(args[i:])
            else:
                # Only thing left is a dict
                if len(args[i:]) > 1:
                    raise ValueError(
                        f"Can't specify multiple arguments for map argument "
                        f"{Hook.__fields__[hook_args[i]]}."
                    )
                value = args[i]
            hook_dict[hook_args[i]] = value
            return
        else:
            # The hooks arguments are indexed
            try:
                hook_dict[hook_args[i]] = v
            except IndexError:
                raise UnknownArgumentException(f"Unknown argument {i}.")


def handle_leading_brackets(args) -> list:
    """
    Handler for cases where we have a hook call with a renderable string as the first
    argument which we rewrite as a var hook. For instance `foo->: foo-{{ bar }}-baz`
    would be rewritten as `foo->: var foo-{{bar}}-baz`.
    """
    if '{{' in args[0]:
        # We split up the string before based on whitespace so eval individually
        if '}}' in args[0]:
            # This is single templatable string -> key->: "{{this}}" => args: ['this']
            args.insert(0, 'var')
        else:
            # Situation where we have key->: "{{ this }}" => args: ['{{', 'this' '}}']
            for i in range(1, len(args)):
                if '}}' in args[i]:
                    joined_template = ' '.join(args[: (i + 1)])
                    other_args = args[(i + 1) :]
                    args = ['var'] + [joined_template] + other_args
                    break
    return args


def run_hook(context: 'Context'):
    """
    Run the hook by qualifying the input argument and matching the input params with the
    with the hook's `_args` which are then overlayed into a hook kwargs. Also interprets
    special cases where you have a string or list input of renderable variables.
    """
    if isinstance(context.input_string, str):
        args, kwargs, flags = unpack_args_kwargs_string(context.input_string)
        args = handle_leading_brackets(args)
        first_arg = args[0]
        # Remove first args it will be consumed and no longer relevant
        args.pop(0)

    else:
        # Rare case when an arrow is used to indicate rendering of a list.
        # Only qualified when input is of form `key->: [{{var}},{{var}},...]
        # In this case we need to set the key as an empty list
        nested_set(
            element=context.output_dict,
            keys=context.key_path[:-1] + [context.key_path[-1][:-2]],
            value=[],
        )
        # Iterate over values appending rendered values. Rendered values can be any type
        for i, v in enumerate(context.input_string):
            nested_set(
                element=context.output_dict,
                keys=context.key_path[:-1]
                + [context.key_path[-1][:-2]]
                + [encode_list_index(i)],
                value=render_variable(context, v),
            )
        return

    # Look up the hook from the imported providers
    Hook = get_hook(first_arg, context)

    if Hook is None:
        raise UnknownHookTypeException(f"Hook type-> \"{first_arg}\" unknown.")

    if context.key_path[-1] in ('->', '_>'):
        # We have an expanded or mixed (with args) hook expression and so there will be
        # additional properties in adjacent keys. Trim key_path_block for blocks
        hook_dict = nested_get(
            context.input_dict, context.key_path[:-1][len(context.key_path_block) :]
        ).copy()
        # Need to replace arrow keys as for the time being (pydantic 1.8.2) - multiple
        # aliases for the same field (type) can't be specified so doing this hack
        if '->' in hook_dict:
            hook_dict.pop('->')
        else:
            hook_dict.pop('_>')
    else:
        # Hook is a compact expression - Can only be a string
        hook_dict = {}
        # hook_dict['hook_type'] = nested_get(context.input_dict, context.key_path)
    hook_dict['hook_type'] = first_arg

    # Associate hook arguments provided in the call with hook attributes
    evaluate_args(args, hook_dict, Hook)
    # Add any kwargs
    for k, v in kwargs.items():
        hook_dict[k] = v
    for i in flags:
        hook_dict[i] = True

    # Main parser
    parse_hook(hook_dict, Hook, context)


def handle_empty_blocks(context: 'Context', block_value):
    """
    Handle keys appended with arrows and interpret them as `block` hooks. Value is
    re-written over with a `block` hook to support the following syntax.

    a-key->:
      if: stuff == 'things'
      for: a_list
      foo->: print ...
      bar->: print ...

    to

    a-key:
      ->: block
      if: stuff == 'things'
      for: a_list
      items:
        foo->: print ...
        bar->: print ...

    :param context:
    :param block_key:
    :param block_value:
    :return:
    """
    # Break up key paths
    base_key_path = context.key_path[:-1]
    new_key = [context.key_path[-1][:-2]]
    # Handle embedded blocks which need to have thier key paths adjusted
    # key_path = (base_key_path + new_key)[-len(context.key_path_block) :]
    key_path = (base_key_path + new_key)[len(context.key_path_block) :]

    old_key_path = context.key_path[len(context.key_path_block) :]

    # Over-write the input with an expanded path (ie no arrow in key)
    nested_set(
        element=context.input_dict,
        keys=key_path,
        value=block_value,
    )
    # Add back the arrow with the value set to `block` for the block hook
    arrow = [context.key_path[-1][-2:]]
    nested_set(
        element=context.input_dict,
        keys=key_path + arrow,
        value='block',
    )
    # Remove the old key
    try:
        nested_delete(context.input_dict, old_key_path)
    except Exception as e:
        print()
        raise e

    # Iterate through the block keys except for the reserved keys like `for` or `if`
    aliases = [v.alias for _, v in BaseHook.__fields__.items()] + ['->', '_>']
    for k, v in block_value.copy().items():
        if k not in aliases:
            # Set the keys under the `items` key per the block hook's input
            nested_set(
                element=context.input_dict,
                keys=key_path + ['items', k],
                value=v,
            )
            # Remove the old key
            nested_delete(context.input_dict, key_path + [k])
        elif context.verbose:
            warnings.warn(f"Warning - skipping over {k} in block hook.")

    # Finally check if the `items` key exists in the input_dict.  If not then we have
    # an empty hook which will cause an ambiguous ValidationError for missing field
    if 'items' not in nested_get(context.input_dict, key_path):
        key = get_readable_key_path(context.key_path)
        raise EmptyBlockException(f"Empty hook in key path = {key}")


def walk_sync(context: 'Context', element):
    """
    Traverse an object looking for hook calls and running those hooks. Here we are
    keeping track of which keys are traversed in a list called `key_path` with strings
    as dict keys and byte encoded integers for list indexes.
    """
    if len(context.key_path) != 0:
        # Handle compact expressions - ie key->: hook_type args
        if context.key_path[-1][-2:] in ('->', '_>'):
            context.input_string = element
            run_hook(context)
            if context.key_path[-1][-2:] == '_>':
                # Private hook calls
                context.keys_to_remove.append(
                    context.key_path[:-1] + [context.key_path[-1][:-2]]
                )
            return

    if isinstance(element, dict):
        # Handle expanded expressions - ie key:\n  ->: hook_type args
        if '->' in element.keys():
            # Public hook calls
            context.key_path.append('->')
            context.input_string = element['->']
            run_hook(context)
            context.key_path.pop()
            return
        elif '_>' in element.keys():
            # Private hook calls
            context.key_path.append('_>')
            context.input_string = element['_>']
            run_hook(context)
            context.key_path.pop()
            context.keys_to_remove.append(context.key_path.copy())
            return
        elif element == {}:
            nested_set(element=context.output_dict, keys=context.key_path, value={})
            return

        for k, v in element.copy().items():
            context.key_path.append(k)
            # Special case where we have an empty hook, expanded or compact
            if k[-2:] in ('->', '_>') and (v is None or isinstance(v, dict)):
                # Here we re-write the input to turn empty hooks into block hooks
                handle_empty_blocks(context, v)
                context.key_path[-1] = k[:-2]
                walk_sync(context, v)
                # context.key_path.pop()
            else:
                # Recurse
                walk_sync(context, v)
                context.key_path.pop()
            # context.key_path.pop()
    # Non-hook calls recurse through inputs
    elif isinstance(element, list):
        # Handle empty lists
        if len(element) == 0:
            nested_set(
                element=context.output_dict, keys=context.key_path, value=element
            )
        else:
            for i, v in enumerate(element.copy()):
                context.key_path.append(encode_list_index(i))
                walk_sync(context, v)
                context.key_path.pop()
    else:
        nested_set(element=context.output_dict, keys=context.key_path, value=element)


def run_handler(context, handler_key, handler_value):
    """
    Run a pre/post execution handlers which are either hooks or functions.

    NOTE: This is an experimental feature and may change.
    """
    if handler_key in context.functions:
        """Run functions"""
        function = context.functions[handler_key]
        context.input_dict = function.exec
        walk_sync(context, function.exec.copy())

    elif get_hook(handler_key, context, suppress_error=True):
        Hook = get_hook(handler_key, context)
        hook = Hook(
            **handler_value,
            input_dict=context.input_dict,
            output_dict=context.output_dict,
            no_input=context.no_input,
            providers=context.providers,
        )
        hook.call()
    else:
        raise UnknownHookTypeException()


def update_input_dict_with_kwargs(context: 'Context', kwargs: dict):
    """
    Update the input dict with kwargs which in this context are treated as overriding
    the keys. Takes into account if the key is a hook and replaces that.
    """
    for k, v in kwargs.items():
        if k in context.input_dict:
            context.input_dict.update({k: v})
        elif f"{k}->" in context.input_dict:
            # Replace the keys and value in the same position it was in
            context.input_dict = {
                key if key != f"{k}->" else k: value if key != f"{k}->" else v
                for key, value in context.input_dict.items()
            }


def run_source(context: 'Context', args: list, kwargs: dict, flags: list):
    """
    Take the input dict and impose global args/kwargs/flags with the following logic:
    - Use kwargs/flags as overriding keys in the input_dict
    - Check the input dict if there is a key matching the arg and run that key
      - Additional arguments are assessed as
        - If the call is to a hook directly, then inject that as an argument
        - If the call is to a block of hooks then call the next hook key
    - Otherwise run normally (ie full parsing).

    An exception exists for if the last arg is `help` in which case that level's help
    is called and exited 0.
    """
    # Tackle is called both through the CLI and as a package and so to preserve args /
    # kwargs we
    if context.global_args is not None:
        args = args + context.global_args
        context.global_args = None

    # Global kwargs/flags are immediately consumed and injected into the kwargs/flags
    if context.global_kwargs is not None:
        kwargs.update(context.global_kwargs)
        context.global_kwargs = None

    if context.global_flags is not None:
        kwargs.update({i: True for i in context.global_flags})
        context.global_flags = None

    update_input_dict_with_kwargs(context=context, kwargs=kwargs)

    for i in flags:
        # Process flags by setting key to true
        context.input_dict.update({i: True})

    if len(args) >= 1:
        # TODO: Implement help
        # `help` which will always be the last arg
        # if args[-1] == 'help':
        #     # Calling help will exit 0. End of the line.
        #     run_help(context, context.input_dict, args[:-1])

        # Loop through all args
        for i in args:
            # Remove any arrows on the first level keys
            first_level_compact_keys = [
                k[:-2] for k, _ in context.input_dict.items() if k.endswith('->')
            ]
            if i in first_level_compact_keys:
                arg_key_value = context.input_dict[i + '->']
                if isinstance(arg_key_value, str):
                    # We have a compact hook so nothing else to traverse
                    break

            elif i in context.input_dict:
                context.key_path.append(i)
                walk_sync(context, context.input_dict[i].copy())
                context.key_path.pop()

            elif i in context.provider_hooks:

                raise NotImplementedError
            else:
                raise ValueError(f"Argument {i} not found as key in input.")
        return

    if len(context.input_dict) == 0:
        raise EmptyTackleFileException(
            # TODO improve
            f"Only functions are declared in {context.input_string} tackle file. Must"
            f" provide an argument such as [] or run `tackle {context.input_string}"
            f" help` to see more options."
        )
    else:
        walk_sync(context, context.input_dict.copy())


def function_walk(
    self: Type[BaseFunction],
    input_element: Union[list, dict],
    return_: Union[list, dict] = None,
) -> Any:
    """
    Walk an input_element for a function and either return the whole context or one or
    many returnable string keys. Function is meant to be implanted into a function
    object and called either as `exec` or some other arbitrary method.
    """
    existing_context = self.output_dict.copy()
    existing_context.update(self.existing_context)

    for i in self.function_fields:
        existing_context.update({i: getattr(self, i)})

    tmp_context = Context(
        provider_hooks=self.provider_hooks,
        existing_context=existing_context,
        output_dict={},
        input_dict=input_element,
        key_path=[],
        no_input=self.no_input,
        calling_directory=self.calling_directory,
        calling_file=self.calling_file,
    )
    walk_sync(context=tmp_context, element=input_element.copy())

    if return_:
        if isinstance(return_, str):
            if return_ in tmp_context.output_dict:
                return tmp_context.output_dict[return_]
            else:
                raise Exception(f"Return value '{return_}' is not found in output.")
        elif isinstance(return_, list):
            if isinstance(tmp_context, list):
                raise Exception(f"Can't have list return {return_} for list output.")
            output = {}
            for i in return_:
                # Can only return top level keys right now
                if i in tmp_context.output_dict:
                    output[i] = tmp_context.output_dict[i]
                else:
                    raise Exception(
                        f"Return value '{i}' in return {return_} not found in output."
                    )
            return tmp_context.output_dict[return_]
        else:
            raise NotImplementedError(f"Return must be of list or string {return_}.")
    return tmp_context.output_dict


def create_function_model(
    context: 'Context', func_name: str, func_dict: dict
) -> Type[BaseFunction]:
    """Create a model from the function input dict."""
    if 'extends' in func_dict:
        base_hook = context.provider_hooks[func_dict['extends']]
        func_dict = {**base_hook, **func_dict}
        func_dict.pop('extends')

    # fmt: off
    # Validate raw input params against pydantic object where values will be used later
    function_input = FunctionInput(
        exec_=func_dict.pop('exec') if 'exec' in func_dict else None,
        return_=func_dict.pop('return') if 'return' in func_dict else None,
        args=func_dict.pop('args') if 'args' in func_dict else [],
        render_exclude=func_dict.pop('render_exclude') if 'render_exclude' in func_dict else [],
        # validators_=func_dict.pop('validators') if 'validators' in func_dict else None,
        # methods_=func_dict.pop('methods') if 'methods' in func_dict else None,
    )
    # fmt: on

    new_func = {'hook_type': func_name[:-2], 'function_fields': []}
    # Create function fields from anything left over in the function dict
    for k, v in func_dict.items():
        if isinstance(v, dict):
            new_func[k] = Field(**v)
        elif isinstance(v, (str, int, float, bool)):
            new_func[k] = v
        elif isinstance(v, list):
            new_func[k] = (list, v)
        new_func['function_fields'].append(k)

    Function = create_model(
        func_name[:-2],
        __base__=BaseFunction,
        **new_func,
        **function_input.dict(include={'args', 'render_exclude'}),
    )
    setattr(
        Function,
        'exec',
        partialmethod(function_walk, function_input.exec_, function_input.return_),
    )

    context.env_.filters[func_name[:-2]] = Function(
        existing_context={},
        no_input=context.no_input,
    ).wrapped_exec

    return Function


def extract_functions(context: 'Context'):
    for k, v in context.input_dict.copy().items():
        if re.match(r'.*(<\-|<\_)$', k):
            Function = create_function_model(context, k, v)
            context.provider_hooks[k[:-2]] = Function
            context.input_dict.pop(k)


def extract_base_file(context: 'Context'):
    """Read the tackle file and initialize input_dict."""
    if context.find_in_parent:
        path = find_in_parent(context.input_dir, context.input_file)
        context.input_file = os.path.basename(path)
        context.input_dir = os.path.dirname(path)
    else:
        path = os.path.join(context.input_dir, context.input_file)

    # Preserve the callling file which should be carried over from tackle calls
    if context.calling_file is None:
        context.calling_file = context.input_file

    context.input_dict = read_config_file(path)
    if context.input_dict is None:
        raise EmptyTackleFileException(f"No tackle file found at {path}.")

    if isinstance(context.input_dict, list):
        # Change output to empty list
        context.output_dict = []
    else:
        # TODO: Implement function extractor
        extract_functions(context)

    # Check if there is a hooks directory in the provider being run and import the hooks
    input_dir_contents = os.listdir(context.input_dir)
    if 'hooks' in input_dir_contents:
        with work_in(context.input_dir):
            context.provider_hooks.import_from_path(context.input_dir)

    # TODO: Experimental feature that could be integrated later
    # # Extract handlers
    # for k, v in list(input_dict.items()):
    #     if k.startswith('__'):
    #         # Run pre-execution handlers and remove from input
    #         run_handler(context, k[2:], v)
    #         input_dict.pop(k)
    #     if k.endswith('__'):
    #         # Store post-execution handlers and remove from input
    #         # TODO: Execute post exec handlers
    #         context.post_exec_handlers.append({k[:-2]: v})
    #         input_dict.pop(k)


def import_local_provider_source(context: 'Context', provider_dir: str):
    """
    Import a provider from a path by checking if the provider has a tackle file and
    returning a path.
    """
    context.input_dir = provider_dir
    if context.input_file is None:
        context.input_file = find_tackle_file(provider_dir)

    if context.directory:
        context.input_file = os.path.join(context.input_file, context.directory)

    extract_base_file(context)


def update_source(context: 'Context'):
    """
    Locate the repository directory from a template reference. This is the main parser
    for determining the source of the context and calls the succeeding parsing
    functions. The parsing order has the following order of precedence.

    If the template wasn't given then use the file in that parent directory.
    If the template refers to a zip file or zip url, download / unzip as the context.
    If the template refers to a repository URL, clone it.
    If the template refers to a file, use that as the context.
    """
    args, kwargs, flags = unpack_args_kwargs_string(context.input_string)

    first_arg = args[0]
    # Remove first args it will be consumed and no longer relevant
    args.pop(0)

    # Zipfile
    if first_arg.lower().endswith('.zip'):
        unzipped_dir = unzip(
            zip_uri=first_arg,
            clone_to_dir=settings.tackle_dir,
            no_input=context.no_input,
            password=context.password,  # TODO: RM - Should prompt?
        )
        import_local_provider_source(context, unzipped_dir)
    # Repo
    elif is_repo_url(first_arg):
        provider_dir = get_repo_source(first_arg, context.checkout)
        import_local_provider_source(context, provider_dir)
    # Directory
    elif is_directory_with_tackle(first_arg):
        # Special case where the input is a path to a directory. Need to override some
        # settings that would normally get populated by zip / repo refs. Does not need
        # a file reference as otherwise would be given absolute path to tackle file.
        context.input_file = os.path.basename(find_tackle_file(first_arg))
        context.input_dir = Path(first_arg).absolute()

        # Load the base file into input_dict
        extract_base_file(context)
    # File
    elif is_file(first_arg):
        context.input_file = os.path.basename(first_arg)
        context.input_dir = Path(first_arg).parent.absolute()
        extract_base_file(context)
    # Search in parent
    else:
        # Lastly we check if there is a key in the parent that matches the arg. This is
        # basically the fallback logic but need to raise error right away if the key
        # does not exist so we don't have to catch it with context later.
        tackle_file = find_nearest_tackle_file()
        if tackle_file is None:
            raise UnknownSourceException(f"Could not find source = {first_arg}")

        context.input_file = os.path.basename(tackle_file)
        context.input_dir = Path(tackle_file).parent.absolute()
        extract_base_file(context)

        if first_arg not in context.input_dict:
            raise UnknownSourceException(
                f"Could not find source = {first_arg} or as "
                f"key in parent tackle file."
            )
        args.insert(0, first_arg)

    # We always change directory into the source that is being called. Needs to be this
    # or would be very confusing if writing a provider to always refer to it's own path.
    with work_in(context.input_dir):
        # Main parsing logic
        run_source(context, args, kwargs, flags)
