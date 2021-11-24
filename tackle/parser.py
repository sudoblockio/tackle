# -*- coding: utf-8 -*-

"""Main parsing module for walking down arbitrary data structures and executing hooks."""
from __future__ import print_function
import logging
from PyInquirer import prompt

from pathlib import Path
import os
import inspect
from typing import Type, Any

from tackle.providers import import_with_fallback_install
from tackle.render import render_variable
from tackle.utils.dicts import (
    nested_get,
    nested_set,
    encode_list_index,
    decode_list_index,
    set_key,
)
from tackle.utils.command import unpack_args_kwargs
from tackle.utils import literal_type
from tackle.utils.vcs import get_repo_source
from tackle.utils.files import read_config_file
from tackle.utils.paths import (
    is_repo_url,
    is_file,
)
from tackle.utils.zipfile import unzip
from tackle.models import Context, BaseHook, HookDict, ConfirmHookDict
from tackle.exceptions import (
    HookCallException,
    UnknownHookTypeException,
    InvalidConfiguration,
)
from tackle.settings import settings

logger = logging.getLogger(__name__)


def get_hook(hook_type, context: 'Context', suppress_error: bool = False):
    """
    Get the hook from available providers.

    This function does the following to return the hook:
    1. Check if hook hasn't been imported already
    2. Check if the hook has been declared in a provider's __init__.py's
    `hook_types` field.
    3. Try to import it then fall back on installing the requirements.txt file
    """
    for h in BaseHook.__subclasses__():
        if hook_type == inspect.signature(h).parameters['type'].default:
            return h

    for p in context.providers:
        if hook_type in p.hook_types:
            import_with_fallback_install(p.name, p.path)

    for h in BaseHook.__subclasses__():
        if hook_type == inspect.signature(h).parameters['type'].default:
            return h

    avail_hook_types = [
        inspect.signature(i).parameters['type'].default
        for i in BaseHook.__subclasses__()
    ]
    logger.debug(f"Available hook types = {avail_hook_types}")
    if not suppress_error:
        raise UnknownHookTypeException(
            f"The hook type=\"{hook_type}\" is not available in the providers. "
            f"Run the application with `--verbose` to see available hook types."
        )


def update_global_args(context: 'Context', args: list, kwargs: dict, flags: list):
    """
    Handler for global args, kwargs, and flags when the source is one of zip, repo, or
    directory. Both kwargs and flags update the override dictionary. Args are first
    used to search within the `input_dict` to see if there is a key of that type and
    jumping to that level and then using those arguments inside that hook call.
    """
    # context.global_kwargs = kwargs
    # context.global_flags = flags
    for k, v in kwargs:
        context.override_inputs.update({k: v})

    for i in flags:
        context.override_inputs.update({i: True})

    # TODO: Implement key seeking logic
    # context.global_args = args


def find_tackle_file(provider_dir):
    provider_contents = os.listdir(provider_dir)
    for i in provider_contents:
        if i in ['tackle.yaml', 'tackle.yml', '.tackle.yaml', '.tackle.yml']:
            return os.path.join(provider_dir, i)

    raise InvalidConfiguration


def get_base_file(context: 'Context'):
    import copy

    context.input_dict = read_config_file(
        os.path.join(context.repo_dir, context.context_file)
    )
    context.output_dict = copy.deepcopy(context.input_dict)


def import_local_provider_source(context: 'Context', provider_dir: str):
    """Imports a provider from a path by checking if the"""
    context.repo_dir = provider_dir
    if context.context_file is None:
        context.context_file = find_tackle_file(provider_dir)

    if context.directory_:
        context.context_file = os.path.join(context.context_file, context.directory_)

    get_base_file(context)


def update_source(context: 'Context'):
    """
    Locate the repository directory from a template reference. This is the main parser
    for determining the source of the context and calls the succeeding parsing
    functions. The parsing order has the following order of precedence.

    If the template refers to a zip file or zip url, download / unzip as the context.
    If the template refers to a repository URL, clone it.
    If the template refers to a file, use that as the context.
    If the template refers to a hook, run that hook with arguments inserted.
    If the template is a path to a local repository, use it.
    """
    if context.input_string is None:
        # TODO: This is a patch as depending on the context we want to default to a given
        # param.  So if it is None, check if tackle in dir, out of dir, etc...
        # Thos would be it?
        context.input_string = '.'
    args, kwargs, flags = unpack_args_kwargs(context.input_string)

    # The first arg determines the source
    if len(args) == 0:
        args.append(".")

    first_arg = args[0]

    # Remove first args it will be consumed and no longer relevant
    args.pop(0)

    # Zipfile
    if first_arg.lower().endswith('.zip'):
        unzipped_dir = unzip(
            zip_uri=first_arg,
            clone_to_dir=settings.tackle_dir,
            no_input=context.no_input,
            password=context.password_,  # TODO: RM - Should prompt?
        )
        import_local_provider_source(context, unzipped_dir)
        # TODO: Fix this
        # context.cleanup = True
        walk_sync(context=context, element=context.input_dict)
        return
    # Repo
    elif is_repo_url(first_arg):
        import_local_provider_source(
            context, get_repo_source(first_arg, context.version_)
        )
        walk_sync(context=context, element=context.input_dict.copy())
        return

    # File
    elif is_file(first_arg):
        # Special case where the input is a path to a file. Need to override some
        # settings that would normally get populated by zip / repo refs
        context.context_file = os.path.basename(first_arg)
        context.repo_dir = Path(first_arg).parent.absolute()

        # Load the base file into input_dict
        get_base_file(context)

        # Main parsing logic
        walk_sync(context=context, element=context.input_dict.copy())
        return

    # Calling a hook directly
    elif get_hook(first_arg, context, suppress_error=True):
        """Main entrypoint to hook parsing logic. All hook calls are funneled here."""

        if context.key_path[-1] in ('->', '_>'):
            hook_value = nested_get(context.input_dict, context.key_path[:-1])

            # Need to replace these keys as for the time being (pydantic 1.8.2) -
            # multiple aliases can't be specified so doing this hack
            if '->' in hook_value:
                hook_value['hook_type'] = hook_value['->']
                hook_value.pop('->')
            else:
                hook_value['hook_type'] = hook_value['_>']
                hook_value.pop('_>')
        else:
            hook_value = nested_get(context.input_dict, context.key_path)

        if isinstance(hook_value, dict):
            context.hook_dict = HookDict(**hook_value)
        else:
            context.hook_dict = HookDict()

        # Set the args which will be overlayed with the `evaluate_args` function later
        # that will override various parameters set within `_args` in the hook def.
        context.hook_dict._args = args
        # Set any kwars from the hook call - ie `->: somehook --if 'key.a_value == 2'`
        for k, v in kwargs.items():
            setattr(context.hook_dict, k, v)

        # Set the hook_type
        context.hook_dict.hook_type = first_arg

        # Parse for any loops / conditionals
        parse_hook(context)
        return

    from tackle.exceptions import UnknownHookTypeException

    # TODO: Raise better error
    raise UnknownHookTypeException


def raise_hook_validation_error(e, Hook, context: 'Context'):
    """Raise more clear of an error when pydantic fails to parse an object."""
    if 'extra fields not permitted' in e.__repr__():
        # Return all the fields in the hook by removing all the base fields.
        context_base_keys = (
            BaseHook(input_string='tmp', type=context.hook_dict.hook_type).dict().keys()
        )

        fields = '--> ' + ', '.join(
            [
                i
                for i in Hook(input_string='tmp').dict().keys()
                if i not in context_base_keys and i != 'type'
            ]
        )
        error_out = (
            f"Error: The field \"{e.raw_errors[0]._loc}\" is not permitted in "
            f"file=\"{context.context_file}\" and key_path=\"{context.key_path}\".\n"
            f"Only values accepted are {fields}, (plus base fields --> "
            f"type, when, loop, chdir, merge)"
        )
        raise HookCallException(error_out)
    else:
        raise e


def set_hook(context: 'Context', Hook: Type[BaseHook], index: int, value):
    """Handles setting the hooks values as literal types and renders fields by default."""
    if 'render_by_default' in Hook.__fields__[Hook._args[index]].field_info.extra:
        if Hook.__fields__[Hook._args[index]].field_info.extra['render_by_default']:
            # Will be rendered with the rest of the variables
            value = render_variable(context, "{{" + value + "}}")
            setattr(context.hook_dict, Hook._args[index], value)
            return
    # literal_type converts string to typed var
    setattr(context.hook_dict, Hook._args[index], literal_type(value))


def evaluate_args(
    context: 'Context',
    Hook: Type[BaseHook],
):
    """
    Associate hook arguments provided in the call with hook attributes. Parses the
    hook's `_args` attribute to know how to map arguments are mapped to where and
    deal with rendering by default.
    """
    for i, v in enumerate(context.hook_dict._args):
        # Iterate over the input args
        if i + 1 == len(Hook._args):
            # We are at the last argument mapping so we need to join the remaining
            # arguments as a single string. Was parsed on spaces so reconstructed.
            if (
                isinstance(
                    Hook.__fields__[Hook._args[i]], (str, float, int, bool, bytes)
                )
                or Hook.__fields__[Hook._args[i]].type_ == Any
            ):
                value = ''.join(context.hook_dict._args[i:])
            elif isinstance(Hook.__fields__[Hook._args[i]], list):
                # If list then remaining items
                value = context.hook_dict._args[i:]
            else:
                # Only thing left is a dict
                if len(context.hook_dict._args[i:]) > 1:
                    raise ValueError(
                        f"Can't specify multiple arguments for map argument "
                        f"{Hook.__fields__[Hook._args[i]]}."
                    )
                value = context.hook_dict._args[i]
                # Join everything up as a list as it doesn't make sense to do anything
                # else at this point.

            set_hook(context, Hook, i, value)
            return
        else:
            # The hooks arguments are indexed
            set_hook(context, Hook, i, v)


def run_hook(context: 'Context', hook_type: str = None):
    """
    Get and call the hook. Handles duplicate keys by removing them from the hook
    instantiation / call.
    """
    Hook = get_hook(context.hook_dict.hook_type, context)
    # Arguments from call are associated with arguments in the hook
    evaluate_args(context, Hook)
    try:
        # Take the items out of the global context and mode if they are declared in the
        # hook dict. This establishes a precedence that attributes declared in the hook
        # are used when running the hook instead of items declared in the context.
        # import time
        # time_start = time.time()

        hook_exclude = {i for i in HookDict.__fields__}
        hook_exclude.update({'_args', '_kwargs', '_flags'})
        hook_context = context.hook_dict.dict(exclude=hook_exclude)
        context_exclude = {i for i in hook_context}
        context_exclude.add('env')
        hook = Hook(**hook_context, **context.dict(exclude=context_exclude))

        hook_output = hook.call()

        # x = time.time() - time_start
        # print(x)

        return hook_output

    except Exception as e:
        # TODO: Do a more graceful shut down - ie raise HookCallException and catch it later?
        raise e


def evaluate_confirm(context: 'Context'):
    """
    Confirm the user wants to do something before an important step.

    Runs with the `confirm` key which can be one of:
    bool - Generic confirmation
    string - Message for confirmation
    dict - Extra params:
        when: Evaluate as boolean
        message: The message to confirm with
        default: True or false as default to confirm
    """
    if context.hook_dict.confirm is None:
        return

    if isinstance(context.hook_dict.confirm, bool):
        # Override bool with generic message.
        if context.hook_dict.confirm:
            context.hook_dict.confirm = "Are you sure you want to do this?"
    if isinstance(context.hook_dict.confirm, str):
        return prompt(
            [
                {
                    'type': 'confirm',
                    'name': 'tmp',
                    'message': context.hook_dict.confirm,
                }
            ]
        )['tmp']
    elif isinstance(context.hook_dict.confirm, dict):
        when_condition = True
        confirm_hook_dict = ConfirmHookDict(**context.hook_dict.confirm)
        # if 'when' in context.hook_dict.confirm:
        if confirm_hook_dict.if_:
            when_condition = evaluate_if(confirm_hook_dict, context)
        if when_condition:
            return prompt(
                [
                    {
                        'type': 'confirm',
                        'name': 'tmp',
                        'message': confirm_hook_dict.message,
                        'default': confirm_hook_dict.default
                        if 'default' in context.hook_dict.confirm
                        else None,
                    }
                ]
            )['tmp']


def evaluate_if(hook_dict: HookDict, context: 'Context') -> bool:
    """Evaluate the when condition and return bool."""
    if context.hook_dict.if_ is None:
        return True

    when_raw = hook_dict.if_
    when_condition = False
    # if isinstance(when_raw, bool):
    #     when_condition = when_raw
    if isinstance(when_raw, str):
        when_condition = render_variable(context, when_raw)
    elif isinstance(when_raw, list):
        # Evaluate lists as successively evalutated 'and' conditions
        for i in when_raw:
            when_condition = render_variable(context, i)
            # If anything is false, then break immediately
            if not when_condition:
                break

    hook_dict.if_ = None

    return when_condition


def evaluate_loop(context: 'Context'):
    """Run the parse_hook function in a loop and return a list of outputs."""
    loop_targets = render_variable(context, context.hook_dict.for_)
    context.hook_dict.for_ = None

    if len(loop_targets) == 0:
        return []

    loop_output = []
    for i, l in (
        enumerate(loop_targets)
        if not context.hook_dict.reverse
        else reversed(list(enumerate(loop_targets)))
    ):
        # Create temporary variables in the context to be used in the loop.
        # TODO: Consider putting this in another dictionary that is looked up based
        #  on inspecting the raw template for refs.
        context.output_dict.update({'index': i, 'item': l})
        # context._index = i
        # context._item = l
        context.key_path.append(encode_list_index(i))
        parse_hook(context, append_key=True)
        context.key_path.pop()
        # loop_output += [parse_hook(context, append_key=True)]

    # # Remove temp variables
    context.output_dict.pop('item')
    context.output_dict.pop('index')
    # context.output_dict[context.key] = loop_output
    # return context.output_dict
    return loop_output
    # output_dict[context.key] = loop_output
    # return output_dict


def parse_hook(
    context: 'Context',
    append_key: bool = False,  # Lets the parser know if it is in a loop
):
    """Parse input dict for loop and when logic and calls hooks."""
    else_object = None
    if context.hook_dict.else_:
        else_object = render_variable(context, context.hook_dict.else_)

    if evaluate_if(context.hook_dict, context):
        # Extract for loop
        if context.hook_dict.for_:
            # This runs the current function in a loop and returns a list of results
            return evaluate_loop(context=context)

        # Block hooks are run independently. This prevents the rest of the hook dict
        # from being rendered ahead of execution.
        if context.hook_dict.hook_type != 'block':
            # TODO: Performance
            # import time
            # time_start = time.time()

            # Render each item of the dictionary
            for k, v in context.hook_dict.dict().items():
                setattr(context.hook_dict, k, render_variable(context, v))

            # x = time.time() - time_start
            # print(x)

        if evaluate_confirm(context):
            return

        # Run the hook
        if context.hook_dict.merge:
            # Merging is for dict outputs only where the entire dict is inserted into
            # the output dictionary.
            to_merge = run_hook(context)
            if not isinstance(to_merge, dict):
                # TODO: Raise better error with context
                raise ValueError(
                    f"Error merging output from key='{context.key_}' in "
                    f"file='{context.context_file}'."
                )
            # context.output_dict.update(to_merge)
            # x = context.key_path[1:]
            for k, v in to_merge.items():
                # nested_set(context.output_dict, context.key_path[1:] + [k], v)
                set_key(context.output_dict, context.key_path[1:] + [k], v)

        else:
            # Normal hook run
            # context.output_dict[context.key], post_gen_hook = run_hook(context)
            # nested_set(context.output_dict, context.key_path, run_hook(context))
            # x = run_hook(context)
            # if append_key:
            #
            # else:
            set_key(
                element=context.output_dict,
                keys=context.key_path,
                value=run_hook(context),
                keys_to_delete=context.remove_key_list,
            )

            # context.key_path.pop()
        # if post_gen_hook:
        #     # TODO: Update this per #4 hook-integration
        #     context.post_gen_hooks.append(post_gen_hook)

        # if append_key:
        #     # TODO: ?
        #     return context.output_dict[context.key_]

    # else:
    #     if else_object is not None:
    #         # Handle the false when condition if there is an `else` param.
    #         # if 'else' in context.hook_dict:
    #         if isinstance(else_object, dict):
    #             # If it is a dict, run it as another hook if type key exists, otherwise
    #             # fallback to dict
    #             if 'type' in else_object:
    #                 # context.input_dict[context.context_key][context.key] = else_object
    #                 # nested_set(context.output_dict, context.key_path, else_object)
    #                 set_key(context.output_dict, context.key_path, else_object)
    #                 return parse_hook(context, append_key=append_key)
    #
    #         else:
    #             # If list or str return tha actual value
    #             # context.output_dict[context.key] = render_variable(context, else_object)
    #             nested_set(
    #                 context.output_dict,
    #                 context.key_path,
    #                 render_variable(context, else_object),
    #             )
    #
    #             return context.output_dict

    # if context.hook_dict.callback:
    #     # Call a hook var but don't return it's output
    #     # TODO: RM?
    #     context.input_dict[context.context_key][
    #         context.key
    #     ] = context.hook_dict.callback
    #     return parse_hook(context, append_key=append_key)

    return context.output_dict


import re


def is_tackle_hook(value):
    if isinstance(value, bytes):
        return False

    REGEX = re.compile(
        r"""^.*(->|_>)$""",
        re.VERBOSE,
    )
    return bool(REGEX.match(value))


def walk_sync(context: 'Context', element):
    if isinstance(element, str):
        if is_tackle_hook(context.key_path[-1]):

            if len(context.key_path[-1]) == 2:
                context.input_string = element
                update_source(context)
                return

            # context.key_path.append(element)
            # context.key_ = context.key_path[1:]

            context.input_string = element
            update_source(context)
            # context.key_path.pop()
        return

    elif isinstance(element, dict):
        for k, v in element.copy().items():
            context.key_path.append(k)
            walk_sync(context, v)
            context.key_path.pop()

    elif isinstance(element, list):
        for i, v in enumerate(element.copy()):
            context.key_path.append(encode_list_index(i))
            walk_sync(context, v)
            context.key_path.pop()
