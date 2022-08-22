import os
import re
import logging
from pathlib import Path
from functools import partialmethod
from typing import Type, Any, Union, Callable
from pydantic import Field, create_model
from pydantic.main import ModelMetaclass
from collections import OrderedDict
from pydantic import ValidationError
from pydoc import locate
from ruamel.yaml.constructor import CommentedKeyMap, CommentedMap
from ruamel.yaml.parser import ParserError

from tackle.render import render_variable, wrap_jinja_braces
from tackle.utils.dicts import (
    nested_get,
    nested_delete,
    nested_set,
    encode_list_index,
    decode_list_index,
    set_key,
    get_target_and_key,
    smush_key_path,
    get_readable_key_path,
    cleanup_unquoted_strings,
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
from tackle.models import (
    Context,
    BaseHook,
    LazyImportHook,
    BaseFunction,
    FunctionInput,
    LazyBaseFunction,
    BaseContext,
)
from tackle.macros import (
    var_hook_macro,
    blocks_macro,
    compact_hook_call_macro,
    list_to_var_macro,
)

from tackle import exceptions
from tackle.settings import settings

logger = logging.getLogger(__name__)


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


def get_hook(hook_type, context: 'Context') -> Type[BaseHook]:
    """
    Get the hook from providers. Qualify if the hook is a method and if it is a lazy
    hook (ie has requirements that have not been installed), install them.
    """
    if '.' in hook_type:
        # When the hook type has a period in it, we are calling a hook's method. Here we
        # are going to split up the call into methods denoted by periods, and do logic
        # to support inheriting base properties into methods. To do this we need to
        # instantiate the base and use the `function_fields` list to inform which
        # fields will be inherited. See `create_function_model` function for more info.
        hook_parts = hook_type.split('.')

        # Extract the base hook.
        hook_type = hook_parts.pop(0)
        h = context.provider_hooks.get(hook_type, None)
        if h is None:
            exceptions.raise_unknown_hook(context, hook_type)

        # TODO: To support calling python hook methods, put a conditional here to
        #  determine if hook is of type BaseHook / LazyImportHook and perform logic
        #  separate from the declarative hook.
        for method in hook_parts:
            new_hook = None
            try:
                new_hook = h.__fields__[method].default
            except (IndexError, KeyError):
                # Raise error - method not found
                exceptions.raise_unknown_hook(context, method, method=True)

            # Update method with values from base class so that fields can be inherited
            # from the base hook. function_fields is a list of those fields that aren't
            # methods / special vars (ie args, return, etc).
            for i in h.__fields__['function_fields'].default:
                if i not in new_hook.function_dict:
                    # Base method should not override child.
                    new_hook.function_dict[i] = h.__fields__['function_dict'].default[i]

            # Methods that are of type LazyBaseFunction which need to have the base
            # instantiated before getting the hook. Allows nested methods for functions.
            if isinstance(new_hook, LazyBaseFunction):
                new_hook = create_function_model(
                    context=context,
                    func_name=h.__fields__[method].name,
                    func_dict=new_hook.function_dict.copy(),
                )

            h = new_hook

    else:
        h = context.provider_hooks.get(hook_type, None)
    if h is None:
        # Raise exception for unknown hook
        exceptions.raise_unknown_hook(context, hook_type)

    # LazyImportHook in hook ref when declared in provider __init__.hook_types
    elif isinstance(h, LazyImportHook):
        # Install the requirements which will convert all the hooks in that provider
        #  to actual hooks
        context.provider_hooks.import_with_fallback_install(
            mod_name=h.mod_name,
            path=h.hooks_path,
        )
        h = context.provider_hooks[hook_type]
    # TODO: Refactor this whole function so this is not repeated
    #  Make it so hook is split right away and evaluated in one loop
    elif isinstance(h, LazyBaseFunction):
        h = create_function_model(
            context=context,
            func_name=hook_type,
            func_dict=h.function_dict.copy(),
        )

    return h


def evaluate_for(hook_dict: dict, Hook: ModelMetaclass, context: 'Context'):
    """Run the parse_hook function in a loop and return a list of outputs."""
    loop_targets = render_variable(context, wrap_jinja_braces(hook_dict['for']))

    if len(loop_targets) == 0:
        return

    hook_dict.pop('for')

    # Need add an empty list in the value so we have something to append to
    target_context, key_path = get_target_and_key(context)
    nested_set(target_context, key_path, [])

    # Account for nested contexts and justify the new keys based on the key path within
    #  blocks by trimming the key_path_block from the key_path.
    if len(context.key_path_block) != 0:
        tmp_key_path = context.key_path[
            len(context.key_path_block) - len(context.key_path) :
        ]  # noqa
        if context.temporary_context is None:
            context.temporary_context = {} if isinstance(tmp_key_path[0], str) else []
        tmp_key_path = [i for i in tmp_key_path if i not in ('->', '_>')]
        nested_set(context.temporary_context, tmp_key_path, [])

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
        parse_hook(hook_dict.copy(), Hook, context, append_hook_value=True)
        context.key_path.pop()

    # Remove temp variables
    try:
        context.existing_context.pop('item')
        context.existing_context.pop('index')
    except KeyError:
        pass


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
    context: Context,
    append_hook_value: bool = False,
):
    """
    Block hooks have already written to the output dict so to merge, need to take the
     keys from the key path and move them up one level.
    """
    if append_hook_value:
        # TODO: https://github.com/robcxyz/tackle-box/issues/66
        #  Allow merging into lists
        if isinstance(context.key_path_block[-1], bytes):
            # An exception maybe needed here or this error is snubbed.
            pass
        raise exceptions.AppendMergeException(
            "Can't merge from for loop.", context=context
        )

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
    if append_hook_value:
        raise exceptions.AppendMergeException(
            "Can't merge from for loop.", context=context
        )

    if context.key_path[-1] in ('->', '_>'):
        # Expanded key - Remove parent key from key path
        key_path = context.key_path[:-2] + [context.key_path[-1]]
    else:
        # Compact key
        key_path = context.key_path[:-1] + [context.key_path[-1][-2:]]

    # Can't merge into top level keys without merging k/v individually
    if len(key_path) == 1:
        # This is only valid for dict output
        if isinstance(hook_output_value, (dict, OrderedDict)):
            for k, v in hook_output_value.items():
                set_key(context=context, value=v, key_path=[k] + key_path)
            return
        else:
            raise exceptions.TopLevelMergeException(
                "Can't merge non maps into top level keys.", context=context
            )
    else:
        if isinstance(hook_output_value, dict):
            for k, v in hook_output_value.items():
                set_key(context=context, value=v, key_path=key_path + [k])
            return
        else:
            set_key(context=context, value=hook_output_value, key_path=key_path)


def run_hook_in_dir(hook: Type[BaseHook]) -> Any:
    if hook.chdir:
        path = os.path.abspath(os.path.expanduser(hook.chdir))
        if os.path.isdir(path):
            # Use contextlib to switch dirs
            with work_in(os.path.abspath(os.path.expanduser(hook.chdir))):
                return hook.exec()
        else:
            raise exceptions.HookUnknownChdirException(
                f"The specified path='{path}' to change to was not found.",
                hook=hook,
            )
    else:
        return hook.exec()


def render_hook_vars(hook_dict: dict, Hook: ModelMetaclass, context: 'Context'):
    """Render the hook variables."""
    for key, value in list(hook_dict.items()):
        if key not in Hook.__fields__ and key not in BASE_METHODS:
            # If the hook has a `kwargs` field, then map it to that field.
            if Hook.__fields__['kwargs'].default is not None:
                default_kwargs = Hook.__fields__['kwargs'].default
                if default_kwargs not in hook_dict:
                    hook_dict[default_kwargs] = {}
                hook_dict[default_kwargs][key] = value
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
            )

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
            #  https://github.com/robcxyz/tackle-box/issues/80
            #  Fixing with custom Field def should fix this.
            elif 'render_by_default' in Hook.__fields__[key].field_info.extra:
                hook_dict[key] = render_variable(context, wrap_jinja_braces(value))

            elif '{{' in value and '}}' in value:
                hook_dict[key] = render_variable(context, value)

        elif isinstance(value, (list, dict)):
            hook_dict[key] = render_variable(context, value)


def parse_sub_context(
    context: 'Context', hook_dict: dict, target: str, append_hook_value: bool = None
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
            append_hook_value=append_hook_value,
        )
        return
    elif isinstance(hook_target, (bool, int, float)):
        set_key(
            context=context,
            value=hook_target,
            append_hook_value=append_hook_value,
        )
        return

    indexed_key_path = context.key_path[
        -(len(context.key_path) - len(context.key_path_block)) :
    ]

    if isinstance(indexed_key_path[-1], bytes):
        # We are in a for loop so we need
        input_dict = nested_get(
            element=context.input_context,
            keys=indexed_key_path[:-3],
        )
        updated_item = [
            hook_dict[target] if i == decode_list_index(context.key_path[-1]) else None
            for i in range(decode_list_index(context.key_path[-1]) + 1)
        ]
        input_dict[indexed_key_path[-3]] = updated_item
        walk_sync(
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
        walk_sync(context, element=input_dict[indexed_key_path[-2]])


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

            try:
                hook = Hook(
                    **hook_dict,
                    input_context=context.input_context,
                    public_context=context.public_context,
                    private_context=context.private_context,
                    temporary_context=context.temporary_context,
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
                        f"https://robcxyz.github.io/tackle-box/providers/"
                        f"{provider_doc_url_str}/{hook_dict['hook_type']}/"
                    )
                raise exceptions.HookParseException(str(msg), context=context) from None

            # Main exec logic
            if hook.try_:
                try:
                    hook_output_value = run_hook_in_dir(hook)
                except Exception as e:
                    if hook.verbose:
                        print(e)
                    if hook.except_:
                        parse_sub_context(context, hook_dict, target='except')
                    return
            else:
                # Normal hook run
                hook_output_value = run_hook_in_dir(hook)

            if hook.skip_output:
                if hook.merge:
                    merge_block_output(
                        hook_output_value=hook_output_value,
                        context=context,
                        append_hook_value=append_hook_value,
                    )
                return
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
    hook's `_args` attribute to know how to map arguments are mapped to where and
    deal with rendering by default.

    TODO: This needs to be re-thought. Right now we parse the inputs without regard
     for the types of the argument mapping. What could be better is if we know the types
     of the arg mapping ahead of time and then try to assemble the most logical mapping
     afterwards. So if the mapping consists of a [str, list], then the if the first
     args are strs then we can ignore the list part. Right now it would just join all
     the strings together if they are part of last arg mapping.
    TODO: Improve error handling.
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
            elif Hook.__fields__[hook_args[i]].type_ == str:
                # Was parsed on spaces so reconstructed.
                value = ' '.join(args[i:])
            elif Hook.__fields__[hook_args[i]].type_ in (bool, float, int):
                # TODO: Incomplete
                value = args[i]
            elif isinstance(Hook.__fields__[hook_args[i]], list):
                # If list then all the remaining items
                value = args[i:]
            elif isinstance(v, str):
                # Make assumption the rest of the args can be reconstructed as above
                value = ' '.join(args[i:])
            elif isinstance(v, (bool, float, int)):
                # TODO: Incomplete
                if len(args[i:]) > 1:
                    value = args[i:]
                else:
                    value = args[i]
            else:
                # Only thing left is a dict
                if len(args[i:]) > 1:
                    raise exceptions.HookParseException(
                        f"Can't specify multiple arguments for map argument "
                        f"{Hook.__fields__[hook_args[i]]}.",
                        context=context,
                    )
                value = args[i]
            hook_dict[hook_args[i]] = value
            return
        else:
            # The hooks arguments are indexed
            try:
                hook_dict[hook_args[i]] = v
            except IndexError:
                if len(hook_args) == 0:
                    raise exceptions.UnknownArgumentException(
                        f"The hook {hook_dict['hook_type']} does not take any "
                        f"arguments. Hook argument {v} caused an error.",
                        context=context,
                    )
                else:
                    raise exceptions.UnknownArgumentException(
                        f"The hook {hook_dict['hook_type']} takes the following indexed"
                        f"arguments -> {hook_args} which does not map to the arg {v}.",
                        context=context,
                    )


def run_hook(context: 'Context'):
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

    # Look up the hook from the imported providers
    Hook = get_hook(first_arg, context)

    if context.key_path[-1] in ('->', '_>'):
        # We have an expanded or mixed (with args) hook expression and so there will be
        # additional properties in adjacent keys. Trim key_path_block for blocks
        try:
            hook_dict = nested_get(
                context.input_context,
                smush_key_path(context.key_path[:-1][len(context.key_path_block) :]),
            ).copy()
        except KeyError as e:
            raise exceptions.UnknownHookTypeException(
                f"Key: {e} - Unknown", context=context
            )
        # Need to replace arrow keys as for the time being (pydantic 1.8.2) - multiple
        # aliases for the same field (type) can't be specified so doing this hack
        if '->' in hook_dict:
            hook_dict.pop('->')
        else:
            hook_dict.pop('_>')
    else:
        # Hook is a compact expression - Can only be a string
        hook_dict = {}
    hook_dict['hook_type'] = first_arg

    # Associate hook arguments provided in the call with hook attributes
    evaluate_args(args=args, hook_dict=hook_dict, Hook=Hook, context=context)
    # Add any kwargs
    for k, v in kwargs.items():
        hook_dict[k] = v
    for i in flags:
        hook_dict[i] = True

    # Cleanup any unquoted fields -> common mistake that is hard to debug producing a
    #  nested dict that breaks parsing / hook calls. Ex foo: {{bar}} -> foo: "{{bar}}"
    cleanup_unquoted_strings(hook_dict)

    # Main parser
    parse_hook(hook_dict, Hook, context)


def walk_sync(context: 'Context', element):
    """
    Traverse an object looking for hook calls and running those hooks. Here we are
    keeping track of which keys are traversed in a list called `key_path` with strings
    as dict keys and byte encoded integers for list indexes.
    """
    if len(context.key_path) != 0:
        # Handle compact expressions - ie key->: hook_type args
        # if context.key_path[-1][-2:] in ('->', '_>'):
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
            run_hook(context)
            context.key_path.pop()
            return
        elif '_>' in element.keys():
            # Private hook calls
            context.key_path.append('_>')
            context.input_string = element['_>']
            run_hook(context)
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
                    )

                walk_sync(context, value)
                context.key_path.pop()
            else:
                # Recurse
                walk_sync(context, v)
                context.key_path.pop()
    # Non-hook calls recurse through inputs
    elif isinstance(element, list):
        # Handle empty lists
        if len(element) == 0:
            set_key(context=context, value=element)
        else:
            for i, v in enumerate(element.copy()):
                context.key_path.append(encode_list_index(i))
                walk_sync(context, v)
                context.key_path.pop()
    else:
        set_key(context=context, value=element)


def update_input_context_with_kwargs(context: 'Context', kwargs: dict):
    """
    Update the input dict with kwargs which in this context are treated as overriding
    the keys. Takes into account if the key is a hook and replaces that.
    """
    for k, v in kwargs.items():
        if k in context.input_context:
            context.input_context.update({k: v})
        elif f"{k}->" in context.input_context:
            # Replace the keys and value in the same position it was in
            context.input_context = {
                key if key != f"{k}->" else k: value if key != f"{k}->" else v
                for key, value in context.input_context.items()
            }


def run_source(context: 'Context', args: list, kwargs: dict, flags: list):
    """
    Take the input dict and impose global args/kwargs/flags with the following logic:
    - Use kwargs/flags as overriding keys in the input_context
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

    update_input_context_with_kwargs(context=context, kwargs=kwargs)

    for i in flags:
        # Process flags by setting key to true
        context.input_context.update({i: True})

    if len(args) >= 1:
        # Loop through all args
        for i in args:
            # Remove any arrows on the first level keys
            first_level_compact_keys = [
                k[:-2] for k, _ in context.input_context.items() if k.endswith('->')
            ]
            if i in first_level_compact_keys:
                arg_key_value = context.input_context[i + '->']
                if isinstance(arg_key_value, str):
                    # We have a compact hook so nothing else to traverse
                    break

            elif i in context.input_context:
                context.key_path.append(i)
                walk_sync(context, context.input_context[i].copy())
                context.key_path.pop()

            elif i in context.provider_hooks:
                Hook = context.provider_hooks[i]
                args.pop(-1)
                evaluate_args(args, {}, Hook=Hook, context=context)

                hook_output_value = Hook().exec()
                return hook_output_value
            else:
                raise exceptions.UnknownInputArgumentException(
                    f"Argument {i} not found as key in tackle file.", context=context
                )
        return

    if len(context.input_context) == 0:
        raise exceptions.EmptyTackleFileException(
            # TODO improve -> Should give help by default?
            f"Only functions are declared in {context.input_string} tackle file. Must"
            f" provide an argument such as [] or run `tackle {context.input_string}"
            f" help` to see more options.",
            context=context,
        )
    else:
        walk_sync(context, context.input_context.copy())


def function_walk(
    self: Type[ModelMetaclass],
    input_element: Union[list, dict],
    return_: Union[list, dict] = None,
) -> Any:
    """
    Walk an input_element for a function and either return the whole context or one or
    many returnable string keys. Function is meant to be implanted into a function
    object and called either as `exec` or some other arbitrary method.
    """
    if input_element is None:
        # If there is no `exec` method, input_element is None so we infer that the
        # input fields are to be returned. This is useful if the user would like to
        # validate a dict easily with a function and is the only natural meaning of
        # a function call without an exec method.
        input_element = {}
        for i in self.function_fields:
            input_element[i] = getattr(self, i)

    if self.public_context:
        existing_context = self.public_context.copy()
        existing_context.update(self.existing_context)
    else:
        existing_context = {}

    for i in self.function_fields:
        # TODO: Why? -> test RM
        existing_context.update({i: getattr(self, i)})

    tmp_context = Context(
        provider_hooks=self.provider_hooks,
        existing_context=existing_context,
        public_context={},
        input_context=input_element,
        key_path=[],
        no_input=self.no_input,
        calling_directory=self.calling_directory,
        calling_file=self.calling_file,
    )
    walk_sync(context=tmp_context, element=input_element.copy())

    if return_:
        if isinstance(return_, str):
            if return_ in tmp_context.public_context:
                return tmp_context.public_context[return_]
            else:
                raise exceptions.FunctionCallException(
                    f"Return value '{return_}' is not found " f"in output.",
                    function=self,
                )
        elif isinstance(return_, list):
            if isinstance(tmp_context, list):
                # TODO: This is not implemented (ie list outputs)
                raise exceptions.FunctionCallException(
                    f"Can't have list return {return_} for " f"list output.",
                    function=self,
                )
            output = {}
            for i in return_:
                # Can only return top level keys right now
                if i in tmp_context.public_context:
                    output[i] = tmp_context.public_context[i]
                else:
                    raise exceptions.FunctionCallException(
                        f"Return value '{i}' in return {return_} not found in output.",
                        function=self,
                    )
            return tmp_context.public_context[return_]
        else:
            raise NotImplementedError(f"Return must be of list or string {return_}.")
    return tmp_context.public_context


def create_function_model(
    context: 'Context', func_name: str, func_dict: dict
) -> Type[BaseFunction]:
    """Create a model from the function input dict."""
    if func_dict is None:
        raise exceptions.EmptyFunctionException(
            "Can't have an empty function", context=context, function_name=func_name
        )

    if func_name.endswith(('<-', '<_')):
        func_name = func_name[:-2]

    # Implement inheritance
    if 'extends' in func_dict and func_dict['extends'] is not None:
        base_hook = context.provider_hooks[func_dict['extends']]
        func_dict = {**base_hook().function_dict, **func_dict}
        func_dict.pop('extends')

    # Persisted with object for `extends`. Used later
    function_dict = func_dict.copy()

    # fmt: off
    # Validate raw input params against pydantic object where values will be used later
    exec_ = None
    if 'exec' in func_dict:
        exec_ = func_dict.pop('exec')
    elif 'exec<-' in func_dict:
        exec_ = func_dict.pop('exec<-')

    function_input = FunctionInput(
        exec_=exec_,
        return_=func_dict.pop('return') if 'return' in func_dict else None,
        args=func_dict.pop('args') if 'args' in func_dict else [],
        render_exclude=func_dict.pop(
            'render_exclude') if 'render_exclude' in func_dict else [],
        # TODO: Build validators
        # validators_=func_dict.pop('validators') if 'validators' in func_dict else None,
    )

    # fmt: on
    new_func = {'hook_type': func_name, 'function_fields': [], 'function_methods': []}
    literals = ('str', 'int', 'float', 'bool', 'dict', 'list')  # strings to match
    # Create function fields from anything left over in the function dict
    for k, v in func_dict.items():
        if v is None:
            # TODO: ? -> why skip? Would be ignored. Empty keys mean something right?
            continue

        if k.endswith(('->', '_>')):
            raise NotImplementedError
        elif k.endswith(('<-', '<_')):
            # Implement method which is instantiated later in `get_hook`
            new_func[k[:-2]] = (Callable, LazyBaseFunction(function_dict=v))
            continue

        elif isinstance(v, dict):
            if 'type' in v:
                # TODO: Qualify type in enum -> Type
                type_ = v['type']
                if type_ not in literals:
                    raise exceptions.MalformedFunctionFieldException(
                        f"Function field {k} with type={v} unknown. Must be one of {','.join(literals)}",
                        function_name=func_name,
                        context=context,
                    )
                new_func[k] = (type_, Field(**v))
            elif 'default' in v:
                new_func[k] = (type(v['default']), Field(**v))
            else:
                raise exceptions.MalformedFunctionFieldException(
                    f"Function field {k} must have either a `type` or `default` field "
                    f"where the type can be inferred.",
                    function_name=func_name,
                    context=context,
                )
        elif v in literals:
            new_func[k] = (locate(v).__name__, Field(...))
        elif isinstance(v, (str, int, float, bool)):
            new_func[k] = v
        elif isinstance(v, list):
            new_func[k] = (list, v)
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
    for k, v in context.input_context.copy().items():
        if re.match(r'^[a-zA-Z0-9\_]*(<\-|<\_)$', k):

            # TODO: RM arrow and put in associated access modifier namespace

            Function = create_function_model(context, k, v)
            context.provider_hooks[k[:-2]] = Function
            context.input_context.pop(k)


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
        # context.calling_file = path
    context.current_file = path

    try:
        context.input_context = read_config_file(path)
    except FileNotFoundError:
        raise exceptions.UnknownSourceException(
            f"Could not find file in {path}.", context=context
        ) from None
    except ParserError as e:
        raise exceptions.TackleFileInitialParsingException(e) from None

    if context.input_context is None:
        raise exceptions.EmptyTackleFileException(
            f"Tackle file found at {path} is empty.", context=context
        )

    if isinstance(context.input_context, list):
        # Change output to empty list
        context.public_context = []
        context.private_context = []
    else:
        extract_functions(context)
        context.public_context = {}
        context.private_context = {}

    # Import the hooks
    context.provider_hooks.import_from_path(context.input_dir)


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
            )

        context.input_file = os.path.basename(tackle_file)
        context.input_dir = Path(tackle_file).parent.absolute()
        extract_base_file(context)

        if first_arg not in context.input_context:
            context.input_file = first_arg
            raise exceptions.UnknownSourceException(
                f"Could not find source = {first_arg} or as "
                f"key in parent tackle file.",
                context=context,
            )
        args.insert(0, first_arg)

    # We always change directory into the source that is being called. Needs to be this
    # or would be very confusing if writing a provider to always refer to it's own path.
    with work_in(context.input_dir):
        # Main parsing logic
        return run_source(context, args, kwargs, flags)
