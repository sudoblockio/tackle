"""
`parser.py` is the core parser for tackle. It does the following steps

- Reads in a tackle provider and loads its / hooks
- Iterate through any keys on the tackle file
  - Perform macros on conditions to
  - Copy input values over to an output dictionary
  - Find hook calls
- Run the hook
  - Perform any logic (if / else / for etc)
  - Call the actual hook
  - Insert the output into the appropriate key within the output context
"""
from collections import OrderedDict
import enum
from functools import partialmethod
import os
from pydantic import Field, create_model, ValidationError
from pydantic.main import ModelMetaclass
from pydantic.fields import ModelField
from pydoc import locate
from pathlib import Path
import re
from ruamel.yaml.constructor import CommentedKeyMap, CommentedMap
from ruamel.yaml.parser import ParserError
import typing
from typing import Type, Any, Union, Callable, Optional

from tackle import exceptions
from tackle.hooks import (
    import_from_path,
    import_with_fallback_install,
    LazyBaseFunction,
    LazyImportHook,
)
from tackle.macros import (
    var_hook_macro,
    blocks_macro,
    compact_hook_call_macro,
    list_to_var_macro,
    function_field_to_parseable_macro,
)
from tackle.models import (
    Context,
    BaseHook,
    BaseFunction,
    FunctionInput,
    BaseContext,
)
from tackle.render import render_variable
from tackle.settings import settings
from tackle.utils.dicts import (
    get_readable_key_path,
    get_set_temporary_context,
    get_target_and_key,
    nested_get,
    nested_delete,
    nested_set,
    encode_list_index,
    decode_list_index,
    set_key,
    remove_arrows_from_key_path,
    cleanup_unquoted_strings,
)
from tackle.utils.command import unpack_args_kwargs_string
from tackle.utils.files import read_config_file
from tackle.utils.help import run_help
from tackle.utils.imports import get_public_or_private_hook
from tackle.utils.render import wrap_jinja_braces
from tackle.utils.paths import (
    work_in,
    is_repo_url,
    is_directory_with_tackle,
    is_file,
    find_tackle_file,
    find_nearest_tackle_file,
    find_in_parent,
)
from tackle.utils.vcs import get_repo_source
from tackle.utils.zipfile import unzip

BASE_METHODS = [
    'if',
    'when',
    'else',
    'for',
    'reverse',
    'try',
    'except',
    'chdir',
    'merge',
]


def get_hook(
    context: 'Context',
    hook_type: str,
    args: list,
    kwargs: dict,
) -> Optional[Type[BaseHook]]:
    """Gets the hook from the context and calls enrich_hook."""
    hook = get_public_or_private_hook(context=context, hook_type=hook_type)
    if hook is None:
        return None
    return enrich_hook(
        context=context,
        hook=hook,
        args=args,
        kwargs=kwargs,
    )


def enrich_hook(
    context: 'Context',
    hook: ModelMetaclass,
    args: list,
    kwargs: dict,
) -> Type[BaseHook]:
    """
    Take a hook and enrich it by lining up the args with potential methods / hook args /
     kwargs. For methods, it recognizes the arg is a method, compiles the method hook
     with the attributes of the base hook making it inherit them.
    """
    # This gets hit when you use an imported declarative hook
    if isinstance(hook, LazyBaseFunction):
        hook = create_function_model(
            context=context,
            func_name=context.input_string,
            func_dict=hook.function_dict.copy(),
        )
    elif isinstance(hook, LazyImportHook):
        import_with_fallback_install(
            context=context,
            mod_name=hook.mod_name,
            path=hook.hooks_path,
        )
        hook = get_public_or_private_hook(context=context, hook_type=hook.hook_type)

    # Handle args
    for n, arg in enumerate(args):
        # If help and last arg
        if arg == 'help' and n == len(args):
            run_help(context, hook)

        # When arg inputs are not hashable then they are actual arguments which will be
        # consumed later
        elif isinstance(arg, (list, dict)):
            # TODO: Check how this logic works with `args` condition below which works
            #  for bypassing the processing of args for later logic
            pass

        # If arg in methods, compile hook
        elif arg in hook.__fields__ and hook.__fields__[arg].type_ == Callable:
            method = hook.__fields__[arg].default
            # Update method with values from base class so that fields can be inherited
            # from the base hook. function_fields is a list of those fields that aren't
            # methods / special vars (ie args, return, etc).
            for i in hook.__fields__['function_fields'].default:
                # Base method should not override child.
                if i not in method.function_dict:
                    method.function_dict[i] = hook.__fields__['function_dict'].default[
                        i
                    ]
                    if method.function_fields is None:
                        method.function_fields = []
                    method.function_fields.append(i)

            # Methods are of type LazyBaseFunction which need to have the base
            # instantiated before getting the hook. Allows nested methods for functions.
            # if isinstance(method, LazyBaseFunction):
            method = create_function_model(
                context=context,
                func_name=arg,
                func_dict=method.function_dict.copy(),
            )
            # args = args[1:]
            args.pop(0)
            hook = method

            if len(args) != 0:
                return enrich_hook(
                    context=context, hook=method, args=args, kwargs=kwargs
                )
        elif 'args' in hook.__fields__:
            # The hook takes positional args
            pass
        else:
            raise exceptions.UnknownInputArgumentException(
                f"Unknown arg supplied `{arg}`",
                context=context,
            )

    # Handle kwargs
    for k, v in kwargs.items():
        if k == 'args':
            # TODO: I thought this would work
            # args.append(v)
            # But just passing works. Reason is the above duplicates the arg. No idea...
            pass
        elif k == 'kwargs':
            pass
        elif k in hook.__fields__:
            # TODO: consolidate with `update_hook_with_kwargs_and_flags` - same same
            if hook.__fields__[k].type_ == bool:
                # Handle flags where default is true
                if hook.__fields__[k].default:
                    hook.__fields__[k].default = False
                else:
                    hook.__fields__[k].default = True
            else:
                hook.__fields__[k].default = v

    return hook


def merge_block_output(
    hook_output_value: Any,
    context: Context,
    append_hook_value: bool = False,
):
    """
    Block hooks have already written to the output dict so to merge, need to take the
     keys from the key path and move them up one level.
    """
    if append_hook_value:
        # TODO: https://github.com/sudoblockio/tackle/issues/66
        #  Allow merging into lists
        if isinstance(context.key_path_block[-1], bytes):
            # An exception maybe needed here or this error is snubbed.
            pass
        # set_key(context=context, value=hook_output_value)
        raise exceptions.AppendMergeException(
            "Can't merge from for loop.", context=context
        ) from None

    # 66 - Should qualify dict here
    target_context, key_path = get_target_and_key(context)
    indexed_block_output = nested_get(element=hook_output_value, keys=key_path)
    for k, v in indexed_block_output.items():
        element, key_path = get_target_and_key(context)
        nested_set(
            element=target_context,
            keys=key_path[:-1] + [k],
            value=v,
        )
    nested_delete(element=target_context, keys=key_path)


def merge_output(
    hook_output_value: Any,
    context: Context,
    append_hook_value: bool = False,
):
    """Merge the contents into it's top level set of keys."""
    if context.key_path[-1] in ('->', '_>'):
        # Expanded key - Remove parent key from key path
        key_path = context.key_path[:-2] + [context.key_path[-1]]
    else:
        # Compact key
        key_path = context.key_path[:-1] + [context.key_path[-1][-2:]]

    if append_hook_value:
        if isinstance(key_path[-3], bytes):
            # We are merging into a list so we need to keep track of the starting
            # index from which we are merging into, the incremented position.
            incremented_position = encode_list_index(
                decode_list_index(key_path[-3]) + decode_list_index(key_path[-1])
            )
            tmp_key_path = key_path[:-3] + [incremented_position] + [key_path[-2]]
            set_key(context=context, value=hook_output_value, key_path=tmp_key_path)
        elif isinstance(hook_output_value, (str, int, float, bool)):
            raise exceptions.AppendMergeException(
                "Can't merge str/int/float/bool into dict from for loop.",
                context=context,
            ) from None
        elif isinstance(hook_output_value, dict):
            # We are merging into a dict
            for k, v in hook_output_value.items():
                tmp_key_path = key_path[:-3] + [key_path[-2]] + [k]
                set_key(context=context, value=v, key_path=tmp_key_path)
        else:
            raise NotImplementedError("Please raise issue with example if seeing this.")
        return

    # Can't merge into top level keys without merging k/v individually
    if len(key_path) == 1:
        # This is only valid for dict output
        if isinstance(hook_output_value, (dict, OrderedDict)):
            for k, v in hook_output_value.items():
                set_key(context=context, value=v, key_path=[k] + key_path)
        else:
            raise exceptions.TopLevelMergeException(
                "Can't merge non maps into top level keys.", context=context
            ) from None
    else:
        if isinstance(hook_output_value, dict):
            for k, v in hook_output_value.items():
                set_key(context=context, value=v, key_path=key_path + [k])
        else:
            set_key(context=context, value=hook_output_value, key_path=key_path)


def run_hook_in_dir(hook: Type[BaseHook]) -> Any:
    """Run the `exec` method in a dir is `chdir` is specified."""
    if hook.chdir:
        path = os.path.abspath(os.path.expanduser(hook.chdir))
        if os.path.isdir(path):
            # Use contextlib to switch dirs
            with work_in(os.path.abspath(os.path.expanduser(hook.chdir))):
                return hook.exec()  # noqa
        else:
            raise exceptions.HookUnknownChdirException(
                f"The specified path='{path}' to change to was not found.",
                hook=hook,
            ) from None
    else:
        return hook.exec()  # noqa


def render_hook_vars(
    context: 'Context',
    hook_dict: dict,
    Hook: ModelMetaclass,
):
    """Render the hook variables."""
    for key, value in list(hook_dict.items()):
        if key not in Hook.__fields__ and key not in BASE_METHODS:
            # If the hook has a `kwargs` field, then map it to that field.
            if Hook.__fields__['kwargs'].default is not None:
                default_kwargs = Hook.__fields__['kwargs'].default
                if default_kwargs not in hook_dict:
                    hook_dict[default_kwargs] = {}
                hook_dict[default_kwargs][key] = render_variable(context, value)
                hook_dict.pop(key)
                continue

            # Get a list of possible fields for hook before raising error.
            possible_fields = [
                f"{k}: {v.type_.__name__}"
                for k, v in Hook.__fields__.items()
                if k not in BaseHook.__fields__
            ]
            # TODO: Include link to docs -> Will need to also include provider name
            #  and then differentiate between lazy imported hooks which already have the
            #  provider and the ones that don't
            raise exceptions.UnknownInputArgumentException(
                f"Key={key} not in hook={hook_dict['hook_type']}. Possible values are "
                f"{', '.join(possible_fields)}",
                context=context,
            ) from None

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
            # TODO: This causes errors when the field is aliased as the lookup doesn't
            #  work and needs a deeper introspection.
            #  https://github.com/sudoblockio/tackle/issues/80
            #  Fixing with custom Field def should fix this.
            elif 'render_by_default' in Hook.__fields__[key].field_info.extra:
                hook_dict[key] = render_variable(context, wrap_jinja_braces(value))

            elif ('{{' in value and '}}' in value) or ('{%' in value and '%}'):
                hook_dict[key] = render_variable(context, value)

        elif isinstance(value, (list, dict)):
            hook_dict[key] = render_variable(context, value)


def parse_sub_context(
    context: 'Context',
    hook_dict: dict,
    target: str,
):
    """
    Reparse a subcontext as in the case with `else` and `except` where you have to
     handle the negative side of the either `if` or `try`. Works on both looped and
     normal runs by checking the last item in the key path. Then overwrites the input
     with a new context.
    """
    hook_target = hook_dict[target]
    if isinstance(hook_target, str):
        set_key(
            context=context,
            value=render_variable(context, hook_dict[target]),
        )
        return
    elif isinstance(hook_target, (bool, int, float)):
        set_key(
            context=context,
            value=hook_target,
        )
        return

    indexed_key_path = context.key_path[
        (len(context.key_path_block) - len(context.key_path)) :  # noqa
    ]

    if isinstance(indexed_key_path[-1], bytes):
        # We are in a for loop
        input_dict = nested_get(
            element=context.input_context,
            keys=indexed_key_path[:-3],
        )
        updated_item = [
            hook_dict[target] if i == decode_list_index(context.key_path[-1]) else None
            for i in range(decode_list_index(context.key_path[-1]) + 1)
        ]
        # TODO: Figure out wtf is going on here...
        input_dict[indexed_key_path[-3]] = updated_item
        walk_element(
            context,
            element=input_dict[indexed_key_path[-3]][
                decode_list_index(context.key_path[-1])
            ],
        )

    else:
        input_dict = nested_get(
            element=context.input_context,
            keys=indexed_key_path[:-2],
        )
        arrow = context.key_path[-1]
        input_dict[indexed_key_path[-2]] = {arrow: 'block', 'items': hook_dict[target]}
        walk_element(context, element=input_dict[indexed_key_path[-2]])


def new_hook(
    context: 'Context',
    hook_dict: dict,
    Hook: ModelMetaclass,
):
    """Create a new instantiated hook."""
    # TODO: WIP - https://github.com/sudoblockio/tackle/issues/104
    tmp_no_input = None if 'no_input' not in hook_dict else hook_dict.pop('no_input')

    skip_output = Hook.__fields__['skip_output']  # Use later
    try:
        hook = Hook(
            **hook_dict,
            no_input=context.no_input if tmp_no_input is None else tmp_no_input,
            temporary_context={} if skip_output.default else context.temporary_context,
            key_path=context.key_path,
            key_path_block=context.key_path_block,
            input_context=context.input_context,
            public_context=context.public_context,
            private_context=context.private_context,
            existing_context=context.existing_context,
            calling_directory=context.calling_directory,
            current_file=context.input_file,
            calling_file=context.calling_file,
            public_hooks=context.public_hooks,
            private_hooks=context.private_hooks,
            verbose=context.verbose,
            env_=context.env_,
            is_hook_call=True,
            override_context=context.override_context,
        )
    except TypeError as e:
        # TODO: Improve -> This is an error when we have multiple of the same
        #  base attribute. Should not conflict in the future when we do
        #  composition on the context but for now, catching common error.
        # TODO: WIP - https://github.com/sudoblockio/tackle/issues/104
        raise exceptions.UnknownInputArgumentException(
            str(e) + " - Can't assign duplicate base fields.", context=context
        ) from None

    except ValidationError as e:
        # Handle any try / except logic
        if 'try' in hook_dict and hook_dict['try']:
            if 'except' in hook_dict and hook_dict['except']:
                parse_sub_context(context, hook_dict, target='except')
            return

        msg = str(e)
        if Hook.identifier.startswith('tackle.providers'):
            id_list = Hook.identifier.split('.')
            provider_doc_url_str = id_list[2].title()
            # Replace the validated object name (ex PrintHook) with the
            # hook_type field that users would more easily know.
            msg = msg.replace(id_list[-1], f"{hook_dict['hook_type']} hook")

            msg += (
                f"\n Check the docs for more information on the hook -> "
                f"https://sudoblockio.github.io/tackle/providers/"
                f"{provider_doc_url_str}/{hook_dict['hook_type']}/"
            )
        raise exceptions.HookParseException(str(msg), context=context) from None
    return hook


def update_hook_with_kwargs_field(context: 'Context', hook_dict: dict):
    """
    In order to facilitate instantiating objects with dicts, a `kwargs` key can be used
     to load the object. For instance `->: a_hook --kwargs a_dict`
    """
    hook_kwargs = hook_dict.pop('kwargs')
    if isinstance(hook_kwargs, dict):
        hook_dict.update(hook_kwargs)
    elif isinstance(hook_kwargs, str):
        try:
            hook_dict.update(
                render_variable(context=context, raw=wrap_jinja_braces(hook_kwargs))
            )
        except ValueError:
            raise exceptions.UnknownArgumentException(
                "The parameter `kwargs` should be either a map or a string "
                "reference to a map.",
                context=context,
            ) from None
    else:
        raise exceptions.UnknownArgumentException(
            "The parameter `kwargs` should be either a map or a string reference "
            "to a map.",
            context=context,
        ) from None


def parse_hook_execute(
    context: 'Context',
    hook_dict: dict,
    Hook: ModelMetaclass,
    append_hook_value: bool = None,
):
    """Parse the remaining arguments such as try/except and merge"""
    if 'kwargs' in hook_dict:
        update_hook_with_kwargs_field(context=context, hook_dict=hook_dict)

    # Render the remaining hook variables
    render_hook_vars(context=context, hook_dict=hook_dict, Hook=Hook)

    # Instantiate the hook
    hook = new_hook(context=context, hook_dict=hook_dict, Hook=Hook)
    if hook is None:
        return

    # Main exec logic
    if hook.try_:
        try:
            hook_output_value = run_hook_in_dir(hook)
        except Exception as e:
            if hook.verbose:
                print(e)
            if hook.except_:
                parse_sub_context(context=context, hook_dict=hook_dict, target='except')
            return
    else:
        # Normal hook run
        hook_output_value = run_hook_in_dir(hook)

    if hook.skip_output:
        # hook property that is only true for `block`/`match` hooks which write to the
        # contexts themselves, thus their output is normally skipped except for merges.
        if hook.merge:
            # In this case we take the public context and overwrite the current context
            # with the output indexed back one key.
            merge_block_output(
                hook_output_value=hook_output_value,
                context=context,
                append_hook_value=append_hook_value,
            )
        elif context.temporary_context is not None:
            # Write the indexed output to the `temporary_context` as it was only written
            # to the `public_context` and not maintained between items in a list
            if not isinstance(context.key_path[-1], bytes):
                get_set_temporary_context(context)

    elif hook.merge:
        merge_output(
            hook_output_value=hook_output_value,
            context=context,
            append_hook_value=append_hook_value,
        )
    else:
        set_key(
            context=context,
            value=hook_output_value,
        )


def evaluate_for(context: 'Context', hook_dict: dict, Hook: ModelMetaclass):
    """Run the parse_hook function in a loop with temporary variables."""
    loop_targets = render_variable(context, wrap_jinja_braces(hook_dict['for']))
    if len(loop_targets) == 0:
        return
    hook_dict.pop('for')

    # Need add an empty list in the value so we have something to append to except when
    # we are merging.
    if 'merge' not in hook_dict:
        set_key(context=context, value=[])
    elif not hook_dict['merge']:
        set_key(context=context, value=[])

    for i, l in (
        enumerate(loop_targets)
        if not render_variable(context, hook_dict.get('reverse', None))
        else reversed(list(enumerate(loop_targets)))
    ):
        if context.existing_context is None:
            context.existing_context = {}
        # Create temporary variables in the context to be used in the loop.
        context.existing_context.update({'index': i, 'item': l})
        # Append the index to the keypath
        context.key_path.append(encode_list_index(i))

        # Reparse the hook with the new temp vars in place
        parse_hook(
            context=context,
            hook_dict=hook_dict.copy(),
            hook=Hook,
            append_hook_value=True,
        )
        context.key_path.pop()

    # Remove temp variables
    try:
        context.existing_context.pop('item')
        context.existing_context.pop('index')
    except KeyError:
        pass


def parse_hook_loop(
    context: 'Context',
    hook_dict: dict,
    hook: ModelMetaclass,
    append_hook_value: bool = None,
):
    if 'for' in hook_dict:
        # This runs the current function in a loop with `append_hook_value` set so
        # that keys are appended in the loop.
        evaluate_for(context, hook_dict, hook)
    else:
        parse_hook_execute(
            context=context,
            hook_dict=hook_dict,
            Hook=hook,
            append_hook_value=append_hook_value,
        )


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


def parse_hook(
    context: 'Context',
    hook_dict: dict,
    hook: ModelMetaclass,
    append_hook_value: bool = None,
):
    """Parse input dict for loop and when logic and calls hooks."""
    if evaluate_if(hook_dict, context, append_hook_value):
        parse_hook_loop(
            context=context,
            hook_dict=hook_dict,
            hook=hook,
            append_hook_value=append_hook_value,
        )
    elif 'else' in hook_dict:
        parse_sub_context(context, hook_dict, target='else')


def evaluate_args(
    args: list,
    hook_dict: dict,
    Hook: ModelMetaclass,  # noqa
    context: 'BaseContext' = None,  # For error handling
):
    """
    Associate hook arguments provided in the call with hook attributes. Parses the
     hook's `args` attribute to know how to map arguments are mapped to where and
     deal with rendering by default.

    TODO: This needs to be re-thought. Right now we parse the inputs without regard
     for the types of the argument mapping. What could be better is if we know the types
     of the arg mapping ahead of time and then try to assemble the most logical mapping
     afterwards. So if the mapping consists of a [str, list], then if the first
     args are strs then we can ignore the list part. Right now it would just join all
     the strings together if they are part of last arg mapping.
    TODO: Improve error handling.
    Solutions:
    - First try to infer type from arg
        - Single types then into unions?
    - If type cannot be infered (ie Any) then do ast as literal
    """
    # Flag to inform if we are at end of args and need to pop the rest
    pop_all: bool = False

    hook_args: list = Hook.__fields__['args'].default
    for i, v in enumerate(args):
        # Iterate over the input args
        if i + 1 == len(hook_args):
            # We are at the last argument mapping so we need to join the remaining
            # arguments as a single string if it is not a list of another map.
            if not isinstance(args[i], (str, float)):
                # Catch list dict and ints - strings floats and bytes caught later
                value = args[i]
            elif Hook.__fields__[hook_args[i]].type_ == str:
                # Was parsed on spaces so reconstructed.
                value = ' '.join(args[i:])
                pop_all = True
            elif Hook.__fields__[hook_args[i]].type_ in (bool, float, int):
                # TODO: Incomplete
                value = args[i]
            elif isinstance(Hook.__fields__[hook_args[i]], list):
                # If list then all the remaining items
                value = args[i:]
                pop_all = True
            elif isinstance(v, str):
                # Make assumption the rest of the args can be reconstructed as above
                value = ' '.join(args[i:])
                pop_all = True
            elif isinstance(v, (bool, float, int)):
                # TODO: Incomplete
                if len(args[i:]) > 1:
                    value = args[i:]
                    pop_all = True
                else:
                    value = args[i]
            else:
                # Only thing left is a dict
                if len(args[i:]) > 1:
                    raise exceptions.HookParseException(
                        f"Can't specify multiple arguments for map argument "
                        f"{Hook.__fields__[hook_args[i]]}.",
                        context=context,
                    ) from None
                value = args[i]
            hook_dict[hook_args[i]] = value
            if pop_all:
                args.clear()
            else:
                args.pop(0)
            return
        else:
            # The hooks arguments are indexed
            try:
                hook_dict[hook_args[i]] = v
            except IndexError:
                if len(hook_args) == 0:
                    # TODO: Give more info on possible methods
                    hook_name = Hook.identifier.split('.')[-1]
                    if hook_name == '':
                        hook_name = 'default'
                    raise exceptions.UnknownArgumentException(
                        f"The {hook_name} hook does not take any "
                        f"arguments. Hook argument {v} caused an error.",
                        context=context,
                    ) from None
                else:
                    raise exceptions.UnknownArgumentException(
                        f"The hook {hook_dict['hook_type']} takes the following indexed"
                        f"arguments -> {hook_args} which does not map to the arg {v}.",
                        context=context,
                    ) from None


def run_hook_at_key_path(context: 'Context'):
    """
    Run the hook by qualifying the input argument and matching the input params with the
     hook's `_args` which are then overlayed into a hook kwargs. Also interprets
     special cases where you have a string or list input of renderable variables.
    """
    if isinstance(context.input_string, str):
        args, kwargs, flags = unpack_args_kwargs_string(context.input_string)
        args = var_hook_macro(args)
        # Remove first args it will be consumed and no longer relevant
        first_arg = args.pop(0)

    else:
        # Rare case when an arrow is used to indicate rendering of a list.
        # Only qualified when input is of form `key->: [{{var}},{{var}},...]
        # In this case we need to set the key as an empty list
        set_key(context, value=[])

        # Iterate over values appending rendered values. Rendered values can be any type
        for i, v in enumerate(context.input_string):
            set_key(
                context=context,
                value=render_variable(context, v),
                key_path=context.key_path + [encode_list_index(i)],
            )
        return

    if context.key_path[-1] in ('->', '_>'):
        # We have an expanded or mixed (with args) hook expression and so there will be
        # additional properties in adjacent keys. Trim key_path_block for blocks
        try:
            hook_dict = nested_get(
                context.input_context,
                remove_arrows_from_key_path(
                    context.key_path[:-1][len(context.key_path_block) :]
                ),
            ).copy()
        except KeyError as e:
            raise exceptions.UnknownHookTypeException(
                f"Key: {e} - Unknown", context=context
            ) from None
        # Need to replace arrow keys as for the time being (pydantic 1.8.2) - multiple
        # aliases for the same field (type) can't be specified so doing this hack
        if '->' in hook_dict:
            hook_dict.pop('->')
        else:
            hook_dict.pop('_>')
    else:
        # Hook is a compact expression - Can only be a string
        hook_dict = {}

    # Look up the hook from the imported providers
    hook = get_hook(
        context=context,
        hook_type=first_arg,
        args=args,
        kwargs=kwargs,
    )
    if hook is None:
        exceptions.raise_unknown_hook(context, first_arg)

    hook_dict['hook_type'] = hook.__fields__['hook_type'].default

    # `args` can be a kwarg (ie `tackle --args foo`) and is manually added to args var
    if 'args' in kwargs:
        # For calling hooks, you can manually provide the hook with args. Useful for
        # creating declarative hooks that
        hook_args = kwargs.pop('args')
        if isinstance(hook_args, list):
            args += hook_args
        else:
            args += [hook_args]

    # Associate hook arguments provided in the call with hook attributes
    evaluate_args(args=args, hook_dict=hook_dict, Hook=hook, context=context)
    # Add any kwargs
    for k, v in kwargs.items():
        hook_dict[k] = v
    for i in flags:
        hook_dict[i] = True
    # Cleanup any unquoted fields -> common mistake that is hard to debug producing a
    #  nested dict that breaks parsing / hook calls. Ex foo: {{bar}} -> foo: "{{bar}}"
    cleanup_unquoted_strings(hook_dict)

    # Main parser
    parse_hook(
        context=context,
        hook_dict=hook_dict,
        hook=hook,
    )


def walk_element(context: 'Context', element):
    """
    Traverse an object looking for hook calls and running those hooks. Here we are
     keeping track of which keys are traversed in a list called `key_path` with strings
     as dict keys and byte encoded integers for list indexes.
    """
    if len(context.key_path) != 0:
        # Handle compact expressions - ie key->: hook_type args
        ending = context.key_path[-1][-2:]
        if ending in ('->', '_>'):
            if isinstance(element, str):
                element = compact_hook_call_macro(context, element)
            elif isinstance(element, list):
                element = list_to_var_macro(context, element)

    if isinstance(element, dict):
        # Handle expanded expressions - ie key:\n  ->: hook_type args
        if '->' in element.keys():
            # Public hook calls
            context.key_path.append('->')
            context.input_string = element['->']
            run_hook_at_key_path(context)
            context.key_path.pop()
            return
        elif '_>' in element.keys():
            # Private hook calls
            context.key_path.append('_>')
            context.input_string = element['_>']
            run_hook_at_key_path(context)
            context.key_path.pop()
            return
        elif element == {}:
            set_key(context=context, value={})
            return

        for k, v in element.copy().items():

            if isinstance(v, CommentedMap):
                # This is for a common parsing error that messes up values with braces.
                # For instance `stuff->: {{things}}` (no quotes), ruamel interprets as
                # 'stuff': ordereddict([(ordereddict([('things', None)]), None)]) which
                # technically is accurate but generally users would never actually do.
                # Since it is common to forget to quote, this is a helper to try to
                # catch that error and fix it.  Warning -> super hacky....
                if len(v) == 1:
                    value_ = next(iter(v.values()))
                    key_ = next(iter(v.keys()))
                    if value_ is None and isinstance(key_, CommentedKeyMap):
                        if context.verbose:
                            _key_path = get_readable_key_path(context.key_path)
                            msg = f"Handling unquoted template at key path {_key_path}."
                            print(msg)
                        v = "{{" + next(iter(next(iter(v.keys())))) + "}}"

            context.key_path.append(k)
            # Special case where we have an empty hook, expanded or compact
            if k[-2:] in ('->', '_>') and (v is None or isinstance(v, dict)):
                # Here we re-write the input to turn empty hooks into block hooks
                blocks_macro(context)
                context.key_path[-1] = k[:-2]
                value = nested_get(
                    element=context.input_context,
                    keys=context.key_path[
                        (len(context.key_path_block) - len(context.key_path)) :
                    ],
                )
                # Finally check if the `items` key exists in the input_context.  If not
                #  then we have an empty hook which will cause an ambiguous
                #  ValidationError for missing field
                if 'items' not in value:
                    raise exceptions.EmptyBlockException(
                        "Empty block hook.", context=context
                    ) from None

                walk_element(context, value)
                context.key_path.pop()
            else:
                # Recurse
                walk_element(context, v)
                context.key_path.pop()
    # Non-hook calls recurse through inputs
    elif isinstance(element, list):
        # Handle empty lists
        if len(element) == 0:
            set_key(context=context, value=element)
        else:
            for i, v in enumerate(element.copy()):
                context.key_path.append(encode_list_index(i))
                walk_element(context, v)
                context.key_path.pop()
    else:
        set_key(context=context, value=element)


def update_input_context(input_dict: dict, update_dict: dict) -> dict:
    """
    Update the input dict with update_dict which in this context are treated as
     overriding the keys. Takes into account if the key is a hook and replaces that.
    """
    for k, v in update_dict.items():
        if k in input_dict:
            input_dict.update({k: v})
        elif f"{k}->" in input_dict:
            # If value is a dict, recurse into this dict
            if isinstance(v, dict):
                input_dict[f"{k}->"] = update_input_context(
                    input_dict=input_dict[f"{k}->"],
                    update_dict=update_dict[k],
                )
            else:
                # Replace the keys and value in the same position it was in
                input_dict = {
                    key if key != f"{k}->" else k: value if key != f"{k}->" else v
                    for key, value in input_dict.items()
                }
        elif f"{k}_>" in input_dict:
            # Same but for private hooks
            if isinstance(v, dict):
                input_dict[f"{k}->"] = update_input_context(
                    input_dict=input_dict[f"{k}_>"],
                    update_dict=update_dict[k],
                )
            else:
                input_dict = {
                    key if key != f"{k}_>" else k: value if key != f"{k}_>" else v
                    for key, value in input_dict.items()
                }
    return input_dict


def update_hook_with_kwargs_and_flags(hook: ModelMetaclass, kwargs: dict) -> dict:
    """
    For consuming kwargs / flags, once the hook has been identified when calling hooks
     via CLI actions, this function matches the kwargs / flags with the hook and returns
     any unused kwargs / flags for use in the outer context. Note that flags are kwargs
     as they have already been merged by now.
    """
    for k, v in kwargs.copy().items():
        if k in hook.__fields__:
            if hook.__fields__[k].type_ == bool:
                # Flags -> These are evaluated as the inverse of whatever is the default
                if hook.__fields__[k].default:  # ie -> True
                    hook.__fields__[k].default = False
                else:
                    hook.__fields__[k].default = True
            else:
                # Kwargs
                hook.__fields__[k].default = v
            hook.__fields__[k].required = False  # Otherwise will complain
            kwargs.pop(k)
    return kwargs


def run_declarative_hook(
    context: 'Context', hook: ModelMetaclass, args: list, kwargs: dict
) -> Any:
    """
    Given a hook with args, find if the hook has methods and if it does not, apply the
     args to the hook based on the `args` field mapping. Calls the hook.
    """
    kwargs = update_hook_with_kwargs_and_flags(
        hook=hook,
        kwargs=kwargs,
    )

    if kwargs != {}:
        # We were given extra kwargs / flags so should throw error
        hook_name = hook.identifier.split('.')[-1]
        if hook_name == '':
            hook_name = 'default'
        unknown_args = ' '.join([f"{k}={v}" for k, v in kwargs.items()])
        raise exceptions.UnknownInputArgumentException(
            f"The args {unknown_args} not recognized when running the hook/method "
            f"{hook_name}. Exiting.",
            context=context,
        ) from None

    if isinstance(hook, LazyBaseFunction):
        hook = create_function_model(
            context=context,
            func_name=context.input_string,
            func_dict=hook.function_dict.copy(),
        )

    # Handle args
    arg_dict = {}
    num_popped = 0
    for i, arg in enumerate(args.copy()):
        # For running hooks in tackle files (ie not in `hooks` dir), we run this logic
        # as the hook is already compiled.
        if arg in hook.__fields__ and hook.__fields__[arg].type_ == Callable:
            # Consume the args
            args.pop(i - num_popped)
            num_popped += 1

            # Gather the function's dict so it can be compiled into a runnable hook
            func_dict = hook.__fields__[arg].default.function_dict.copy()

            # Add inheritance from base function fields
            for j in hook.__fields__['function_fields'].default:
                # Base method should not override child.
                if j not in func_dict:
                    func_dict[j] = hook.__fields__[j]

            hook = create_function_model(
                context=context,
                func_name=hook.__fields__[arg].name,
                func_dict=func_dict,
            )
        elif isinstance(hook, LazyBaseFunction) and (
            arg + '<-' in hook.function_dict or arg + '<_' in hook.function_dict
        ):
            # Consume the args
            args.pop(i - num_popped)
            num_popped += 1

            # Gather the function's dict so it can be compiled into a runnable hook
            if arg + '<-' in hook.function_dict:
                func_dict = hook.function_dict[arg + '<-']
            else:
                func_dict = hook.function_dict[arg + '<_']

            # Add inheritance from base function fields
            if hook.function_fields is not None:
                for j in hook.function_fields:
                    # Base method should not override child.
                    if j not in func_dict:
                        func_dict[j] = hook.function_dict[j]
            hook = create_function_model(
                context=context,
                func_name=arg,
                func_dict=func_dict,
            )

        elif arg == 'help':
            # Exit 0
            run_help(context=context, hook=hook)

        elif hook.__fields__['args'].default == []:  # noqa
            # Throw error as we have nothing to map the arg to
            hook_name = hook.identifier.split('.')[-1]
            if hook_name == '':
                msg = "default hook"
            else:
                msg = f"hook='{hook_name}'"
            raise exceptions.UnknownInputArgumentException(
                f"The {msg} was supplied the arg='{arg}' and does not take any "
                "arguments. Exiting.",
                context=context,
            ) from None

    # Handle the `args` field which maps to args
    if 'args' in hook.__fields__:
        evaluate_args(args, arg_dict, Hook=hook, context=context)

    try:
        Hook = hook(**kwargs, **arg_dict)
    except ValidationError as e:
        raise exceptions.MalformedFunctionFieldException(
            str(e),
            function_name=hook.identifier.split(".")[-1],
            context=context,
        ) from None
    return Hook.exec()


def raise_if_args_exist(
    context: 'Context', hook: ModelMetaclass, args: list, kwargs: dict, flags: list
):
    """
    Raise an error if not all the args / kwargs / flags have been consumed which would
     mean the user supplied extra vars and should be yelled at.
    """
    # TODO: Refactor into own file

    msgs = []
    if len(args) != 0:
        msgs.append(f"args {', '.join(args)}")
    if len(kwargs) != 0:
        missing_kwargs = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        msgs.append(f"kwargs {missing_kwargs}")
    if len(flags) != 0:
        msgs.append(f"flags {', '.join(flags)}")
    if len(msgs) != 0:
        if hook:
            hook_name = hook.identifier.split('.')[-1]
            if hook_name == '':
                hook_name = 'default'
            raise exceptions.UnknownInputArgumentException(
                # TODO: Add the available args/kwargs/flags to this error msg
                f"The {' and '.join(msgs)} were not found in the \"{hook_name}\" hook. "
                f"Run the same command without the arg/kwarg/flag + \"help\" to see the "
                f"available args/kwargs/flags.",
                context=context,
            ) from None
        else:
            raise exceptions.UnknownSourceException(
                f"Could not find source = {args[0]} or as key / hook in parent tackle "
                f"file.",
                context=context,
            ) from None


def parse_source_args(
    context: 'Context', args: list, kwargs: dict, flags: list
) -> Optional:
    """
    Process global args/kwargs/flags based on if the args relate to the default hook or
     some public hook (usually declarative). Once the hook has been identified, the
     args/kwargs/flags are consumed and if there are any args left, an error is raised.
    """
    # Tackle is called both through the CLI and as a package and so to preserve args /
    # kwargs we merge them here.
    if context.global_args is not None:
        args = args + context.global_args
        context.global_args = None

    # Global kwargs/flags are immediately consumed and injected into the kwargs/flags
    if context.global_kwargs is not None:
        kwargs.update(context.global_kwargs)
        context.global_kwargs = None

    if context.global_flags is not None:
        # TODO: Validate -> These are temporarily set to true but will be resolved as
        #  the inverse of what the default is
        kwargs.update({i: True for i in context.global_flags})
        context.global_flags = None

    # For CLI calls, this logic lines up the args with methods / method args and
    # integrates the kwargs / flags into the call
    if len(args) == 0 and context.default_hook:  # Default hook (no args)
        # TODO: Refactor into own file
        # Add kwargs / flags (already merged into kwargs) to default hook
        kwargs = update_hook_with_kwargs_and_flags(
            hook=context.default_hook,
            kwargs=kwargs,
        )
        # Run the default hook as there are no args. The outer context is then parsed
        #  as otherwise it would be unreachable.
        try:
            default_hook_output = context.default_hook().exec()
        except ValidationError as e:
            raise exceptions.UnknownInputArgumentException(
                e.__str__(), context=context
            ) from None
        # Return the output of the default hook
        # TODO: Determine what the meaning of a primitive type return means with some
        #  kind of outer context -> Should error (and be caught) if there is a conflict
        #  in types.
        context.public_context = default_hook_output
        # TODO: ??? -> If output is primitive, then we need to return it without parsing
        #  the outer context
        raise_if_args_exist(  # Raise if there are any args left
            context=context,
            hook=context.default_hook,
            args=args,
            kwargs=kwargs,
            flags=flags,
        )
    elif len(args) == 1 and args[0] == 'help' and context.default_hook is not None:
        run_help(context=context, hook=context.default_hook)
    elif len(args) == 1 and args[0] == 'help':
        run_help(context=context)
    elif len(args) != 0:  # With args
        # TODO: Refactor into own file
        # Prioritize public_hooks (ie non-default hook) because if the hook exists,
        # then we should consume the arg there instead of using the arg as an arg for
        # default hook because otherwise the public hook would be unreachable.
        if args[0] in context.public_hooks:
            # Search within the public hook for additional args that could be
            # interpreted as methods which always get priority over consuming the arg
            # as an arg within the hook itself.
            public_hook = args.pop(0)  # Consume arg
            context.public_context = run_declarative_hook(
                context=context,
                hook=context.public_hooks[public_hook],
                args=args,
                kwargs=kwargs,
            )
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                hook=context.public_hooks[public_hook],
                args=args,
                kwargs=kwargs,
                flags=flags,
            )
        elif context.default_hook:
            context.public_context = run_declarative_hook(
                context=context, hook=context.default_hook, args=args, kwargs=kwargs
            )
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                hook=context.default_hook,
                args=args,
                kwargs=kwargs,
                flags=flags,
            )
        else:
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                hook=context.default_hook,  # This is None if it does not exist
                args=args,
                kwargs=kwargs,
                flags=flags,
            )
        # We are not going to parse the outer context in this case as we are already
        # within a hook. Doesn't necessarily make sense in this case.
        return
    else:
        # If there are no declarative hooks defined, use the kwargs to override values
        #  within the context.
        context.input_context = update_input_context(
            input_dict=context.input_context,
            update_dict=kwargs,
        )
        # Apply overrides
        context.input_context = update_input_context(
            input_dict=context.input_context,
            update_dict=context.override_context,
        )

    for i in flags:
        # TODO: This should use `update_input_context` as we don't know if the key has
        #  a hook in it -> Right? It has not been expanded...
        # Process flags by setting key to true
        context.input_context.update({i: True})

    if len(context.input_context) == 0:
        if context.public_context is None:
            raise exceptions.EmptyTackleFileException(
                # TODO improve -> Should give help by default?
                f"Only functions are declared in {context.input_string} tackle file. Must"
                f" provide an argument such as [] or run `tackle {context.input_string}"
                f" help` to see more options.",
                context=context,
            ) from None
    else:
        walk_element(context, context.input_context.copy())


def parse_tmp_context(context: Context, element: Any, existing_context: dict):
    """
    Parse an arbitrary element. Only used for declarative hook field defaults and in
     the `run_hook` hook in the tackle provider.
    """
    tmp_context = Context(
        public_hooks=context.public_hooks,
        private_hooks=context.private_hooks,
        public_context={},
        private_context={},
        temporary_context=context.temporary_context,
        existing_context=existing_context,
        input_context=element,
        key_path=['->'],
        key_path_block=['->'],
        no_input=context.no_input,
        calling_directory=context.calling_directory,
        calling_file=context.calling_file,
        # current_file=context.current_file,
        verbose=context.verbose,
        env_=context.env_,
        override_context=context.override_context,
    )
    walk_element(context=tmp_context, element=element)

    return tmp_context.public_context


def get_complex_field(
    field: Any,
) -> Type:
    """
    Takes an input field such as `list[str]` which can include uncalled hooks and calls
     those hooks before returning the  field. Works recursively to find nested hooks
     within types.
    """
    if isinstance(field, list):
        for i, v in enumerate(field):
            field[i] = get_complex_field(v)
    elif isinstance(field, dict):
        for k, v in field.items():
            field[k] = get_complex_field(v)
    elif isinstance(field, BaseFunction):
        field = field.exec()
    return field


def function_walk(
    self: 'Context',
    input_element: Union[list, dict],
    return_: Union[list, dict] = None,
) -> Any:
    """
    Walk an input_element for a function and either return the whole context or one or
     many returnable string keys. Function is meant to be implanted into a function
     object and called either as `exec` or some other arbitrary method.
    """
    if input_element == {}:
        # If there is no `exec` method, input_element is {} so we infer that the
        # input fields are to be returned. This is useful if the user would like to
        # validate a dict easily with a function and is the only natural meaning of
        # a function call without an exec method.
        input_element = {}
        for i in self.function_fields:
            input_element[i] = get_complex_field(getattr(self, i))

    if self.public_context:
        existing_context = self.public_context.copy()
        existing_context.update(self.existing_context)
    else:
        existing_context = {}

    for i in self.function_fields:
        # Update a function's existing context with the already matched args
        value = getattr(self, i)
        if isinstance(value, dict) and '->' in value:
            # For when the default has a hook in it
            output = parse_tmp_context(
                context=self, element={i: value}, existing_context=existing_context
            )
            existing_context.update(output)
            try:
                input_element[i] = output[i]
            except KeyError:
                raise exceptions.FunctionCallException(
                    f"Error parsing declarative hook field='{i}'. Must produce an "
                    f"output for the field's default.",
                    function=self,  # noqa
                ) from None
        else:
            # Otherwise just the value itself
            existing_context.update({i: get_complex_field(getattr(self, i))})

    tmp_context = Context(
        public_hooks=self.public_hooks,
        private_hooks=self.private_hooks,
        existing_context=existing_context,
        public_context={},
        input_context=input_element,
        key_path=[],
        no_input=self.no_input,
        calling_directory=self.calling_directory,
        calling_file=self.calling_file,
        env_=self.env_,
        override_context=self.override_context,
    )
    walk_element(context=tmp_context, element=input_element.copy())

    if return_:
        return_ = render_variable(tmp_context, return_)
        if isinstance(return_, str):
            if return_ in tmp_context.public_context:
                return tmp_context.public_context[return_]
            else:
                raise exceptions.FunctionCallException(
                    f"Return value '{return_}' is not found " f"in output.",
                    function=self,  # noqa
                ) from None
        elif isinstance(return_, list):
            if isinstance(tmp_context, list):
                # TODO: This is not implemented (ie list outputs)
                raise exceptions.FunctionCallException(
                    f"Can't have list return {return_} for " f"list output.",
                    function=self,  # noqa
                ) from None
            output = {}
            for i in return_:
                # Can only return top level keys right now
                if i in tmp_context.public_context:
                    output[i] = tmp_context.public_context[i]
                else:
                    raise exceptions.FunctionCallException(
                        f"Return value '{i}' in return {return_} not found in output.",
                        function=self,  # noqa
                    ) from None
            return tmp_context.public_context[return_]
        else:
            raise NotImplementedError(f"Return must be of list or string {return_}.")
    return tmp_context.public_context


LITERAL_TYPES: set = {'str', 'int', 'float', 'bool', 'dict', 'list'}  # strings to match


def parse_function_type(
    context: Context,
    type_str: str,
    func_name: str,
):
    """
    Parse the `type` field within a declarative hook and use recursion to parse the
     string into real types.
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
            parse_function_type(
                context=context,
                type_str=arg,
                func_name=func_name,
            )
            for arg in re.split(r',(?![^[\]]*])', type_args_str)
        ]
        # Get base type
        base_type = parse_function_type(
            context=context,
            type_str=base_type_str,
            func_name=func_name,
        )

        if len(type_args) == 0:
            return base_type
        elif base_type == typing.Optional:
            # Optional only takes a single arg
            if len(type_args) == 1:
                return base_type[type_args[0]]
            else:
                raise exceptions.MalformedFunctionFieldException(
                    "The type `Optional` only takes one arg.",
                    context=context,
                    function_name=func_name,
                ) from None
        else:
            return base_type[tuple(type_args)]

    # Check if it's a generic type without type arguments
    if hasattr(typing, type_str):
        return getattr(typing, type_str)
    elif type_str not in LITERAL_TYPES:
        hook = get_public_or_private_hook(context=context, hook_type=type_str)
        if hook is None:
            try:
                type_ = getattr(typing, type_str.title())
            except AttributeError:
                raise exceptions.MalformedFunctionFieldException(
                    f"The type `{type_str}` is not recognized. Must be in python's "
                    f"`typing` module.",
                    context=context,
                    function_name=func_name,
                ) from None
            return type_
        elif isinstance(hook, LazyBaseFunction):
            # We have a hook we need to build
            return create_function_model(
                context=context,
                func_name=type_str,
                func_dict=hook.function_dict.copy(),
            )
        else:
            return hook
    # Treat it as a plain name - Safe eval as already qualified as literal
    return eval(type_str)


def function_extends_merge_hook(
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
    return {**base_hook().function_dict, **func_dict}


def function_extends(
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
        return function_extends_merge_hook(
            context=context,
            func_name=func_name,
            func_dict=func_dict,
            extends=extends,
        )

    elif isinstance(extends, list):
        for i in extends:
            if not isinstance(i, str):
                break
            return function_extends_merge_hook(
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


def create_function_model(
    context: 'Context',
    func_name: str,
    func_dict: dict,
) -> Type[BaseFunction]:
    """Create a model from the function input dict."""
    if func_name.endswith(('<-', '<_')):
        func_name = func_name[:-2]

    if func_dict is None:
        raise exceptions.EmptyFunctionException(
            "Can't have an empty function", context=context, function_name=func_name
        )
    if not isinstance(func_dict, dict):
        raise exceptions.MalformedFunctionFieldException(
            "Input to a declarative hook must be a map. This could change in future"
            " versions.",
            context=context,
            function_name=func_name,
        ) from None

    # Macro to expand all keys properly so that a field's default can be parsed
    func_dict = function_field_to_parseable_macro(func_dict, context, func_name)

    # Apply overrides to input fields
    for k, v in context.override_context.items():
        if k in func_dict:
            func_dict[k] = v

    # Implement inheritance
    if 'extends' in func_dict and func_dict['extends'] is not None:
        func_dict = function_extends(
            context=context,
            func_name=func_name,
            func_dict=func_dict,
        )

    # Persisted with object for `extends`. Used later
    function_dict = func_dict.copy()

    # fmt: off
    # Validate raw input params against pydantic object where values will be used later
    exec_ = {}
    if 'exec' in func_dict:
        exec_ = func_dict.pop('exec')
    elif 'exec<-' in func_dict:
        exec_ = func_dict.pop('exec<-')

    # Apply overrides to exec_
    exec_ = update_input_context(
        input_dict=exec_,
        update_dict=context.override_context,
    )

    # Special vars
    function_input = FunctionInput(
        exec_=exec_,
        return_=func_dict.pop('return') if 'return' in func_dict else None,
        args=func_dict.pop('args') if 'args' in func_dict else [],
        render_exclude=func_dict.pop(
            'render_exclude') if 'render_exclude' in func_dict else [],
        help=func_dict.pop('help') if 'help' in func_dict else None,
        # TODO: Build validators
        # validators_=func_dict.pop('validators') if 'validators' in func_dict else None,
    )

    # fmt: on
    new_func = {'hook_type': func_name, 'function_fields': []}

    # First pass through the func_dict to parse out the methods
    for k, v in func_dict.copy().items():
        if k.endswith(('<-', '<_')):
            # Implement method which is instantiated later in `enrich_hook`
            new_func[k[:-2]] = (Callable, LazyBaseFunction(function_dict=v))
            func_dict.pop(k)
            continue

    # Create function fields from anything left over in the function dict
    for k, v in func_dict.items():
        if v is None:
            # TODO: Why skip? Would be ignored. Empty keys mean something right?
            continue

        if k.endswith(('->', '_>')):
            raise NotImplementedError
        elif k.endswith(('<-', '<_')):
            # Implement method which is instantiated later in `enrich_hook`
            new_func[k[:-2]] = (Callable, LazyBaseFunction(function_dict=v))
            continue

        elif isinstance(v, dict):
            if 'enum' in v:
                if 'type' in v:
                    raise exceptions.MalformedFunctionFieldException(
                        'Enums are implicitly typed.',
                        context=context,
                        function_name=func_name,
                    )
                enum_type = enum.Enum(k, {i: i for i in v['enum']})
                if 'default' in v:
                    new_func[k] = (enum_type, v['default'])
                else:
                    new_func[k] = (enum_type, ...)
            elif 'type' in v:
                type_ = v['type']
                if type_ in LITERAL_TYPES:
                    parsed_type = locate(type_).__name__
                else:
                    parsed_type = parse_function_type(
                        context=context,
                        type_str=type_,
                        func_name=func_name,
                    )
                if 'description' in v:
                    v = dict(v)
                    v['description'] = v['description'].__repr__()
                new_func[k] = (parsed_type, Field(**v))
            elif 'default' in v:
                if isinstance(v['default'], dict) and '->' in v['default']:
                    # For hooks in the default fields.
                    new_func[k] = (Any, Field(**v))
                else:
                    new_func[k] = (type(v['default']), Field(**v))
            else:
                new_func[k] = (dict, v)
        elif isinstance(v, str) and v in LITERAL_TYPES:
            new_func[k] = (locate(v).__name__, Field(...))
        elif isinstance(v, (str, int, float, bool)):
            new_func[k] = v
        elif isinstance(v, list):
            new_func[k] = (list, v)
        elif isinstance(v, ModelField):
            # Is encountered when inheritance is imposed and calling function methods
            new_func[k] = (v.type_, v.default)
        else:
            raise Exception("This should never happen")

        # function_fields used later to populate functions without an exec method and
        # the context for rendering inputs.
        new_func['function_fields'].append(k)

    # TODO: Update module namespace
    # Create a function with the __module__ default to pydantic.main
    try:
        Function = create_model(
            func_name,
            __base__=BaseFunction,
            **new_func,
            **function_input.dict(include={'args', 'render_exclude'}),
            **{'function_dict': (dict, function_dict)},  # Preserve for `extends` key
            # https://github.com/sudoblockio/tackle/issues/99
            public_hooks=context.public_hooks,
            private_hooks=context.private_hooks,
            calling_directory=context.calling_directory,
            calling_file=context.calling_file,
            override_context=context.override_context,
            no_input=context.no_input,
            # Causes TypeError in pydantic -> __subclasscheck__
            # env_=context.env_,
        )
    except NameError as e:
        if 'shadows a BaseModel attribute' in e.args[0]:
            shadowed_arg = e.args[0].split('\"')[1]
            extra = "a different value"
            raise exceptions.ShadowedFunctionFieldException(
                f"The function field \'{shadowed_arg}\' is reserved. Use {extra}.",
                function_name=func_name,
                context=context,
            ) from None
        # Don't know what else could happen
        raise e

    # Create an 'exec' method on the function that can be called later.
    setattr(
        Function,
        'exec',
        partialmethod(function_walk, function_input.exec_, function_input.return_),
    )

    # TODO: Rm when filters fixed
    # context.env_.filters[func_name] = Function(
    #     existing_context={},
    #     no_input=context.no_input,
    # ).wrapped_exec

    return Function


def extract_functions(context: 'Context'):
    """
    Iterate through all the keys along baseline of tackle file and extract / compile
     all the keys that reference functions.
    """
    for k, v in context.input_context.copy().items():
        if re.match(r'^[a-zA-Z0-9\_]*(<\-|<\_)$', k):  # noqa
            # TODO: RM arrow and put in associated access modifier namespace
            Function = create_function_model(
                context=context,
                func_name=k,
                func_dict=v,
            )
            function_name = k[:-2]
            arrow = k[-2:]
            if function_name == "":
                # Function is the default hook
                context.default_hook = Function
                context.input_context.pop(k)
            elif arrow == '<-':  # public hook
                context.public_hooks[function_name] = Function
                context.input_context.pop(k)
            elif arrow == '<_':  # private hook
                context.private_hooks[function_name] = Function
                context.input_context.pop(k)
            else:
                raise  # Should never happen


def extract_base_file(context: 'Context'):
    """Read the tackle file and initialize input_context."""
    if context.find_in_parent:
        try:
            path = find_in_parent(context.input_dir, [context.input_file])
        except NotADirectoryError:
            raise exceptions.UnknownSourceException(
                f"Could not find {context.input_file} in {context.input_dir} or in "
                f"any of the parent directories.",
                context=context,
            ) from None
        context.input_file = os.path.basename(path)
        context.input_dir = os.path.dirname(path)
    else:
        path = os.path.join(context.input_dir, context.input_file)

    # Preserve the calling file which should be carried over from tackle calls
    if context.calling_file is None:
        context.calling_file = context.input_file
    context.current_file = path

    try:
        context.input_context = read_config_file(path)
    except FileNotFoundError:
        raise exceptions.UnknownSourceException(
            f"Could not find file in {path}.", context=context
        ) from None
    except ParserError as e:
        raise exceptions.TackleFileInitialParsingException(e) from None  # noqa

    if context.input_context is None:
        raise exceptions.EmptyTackleFileException(
            f"Tackle file found at {path} is empty.", context=context
        ) from None

    # Import the hooks and install requirements.txt if there is a ModuleNotFound error
    import_from_path(context, context.input_dir, skip_on_error=False)

    if isinstance(context.input_context, list):
        # Change output to empty list
        context.public_context = []
        context.private_context = []
    else:
        extract_functions(context)
        context.public_context = {}
        context.private_context = {}


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


def parse_source(context: 'Context'):
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

        # Load the base file into input_context
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
            raise exceptions.UnknownSourceException(
                f"Could not find source = {first_arg}", context=context
            ) from None

        context.input_file = os.path.basename(tackle_file)
        context.input_dir = Path(tackle_file).parent.absolute()
        extract_base_file(context)

        args.insert(0, first_arg)

    # We always change directory into the source that is being called. Needs to be this
    # or would be very confusing if writing a provider to always refer to it's own path.
    with work_in(context.input_dir):
        # Main parsing logic
        return parse_source_args(context, args, kwargs, flags)
