# -*- coding: utf-8 -*-

"""Main parsing module for walking down arbitrary data structures and executing hooks."""
from __future__ import print_function
import logging
from PyInquirer import prompt
from pydantic.error_wrappers import ValidationError
from pathlib import Path
import os
import inspect
import shlex
from typing import List, Type, Any


from tackle.providers import import_with_fallback_install
from tackle.render import render_variable
from tackle.utils.dicts import nested_get, nested_set
from tackle.utils.command import unpack_args_kwargs


from tackle.utils import literal_type
from tackle.utils.vcs import clone
from tackle.utils.paths import (
    is_repo_url,
    is_file,
    repository_has_tackle_file,
    determine_tackle_generation,
)
from tackle.utils.zipfile import unzip
from tackle.models import Context, BaseHook, HookDict, ConfirmHookDict

from tackle.exceptions import (
    RepositoryNotFound,
    HookCallException,
    UnknownHookTypeException,
)
from tackle.settings import settings

logger = logging.getLogger(__name__)


# from tackle.utils.files import load, dump
# if TYPE_CHECKING:
#     from tackle.models import Context


# def strip_dashes(raw_arg: str):
#     while raw_arg.startswith('-'):
#         raw_arg = raw_arg[1:]
#     return raw_arg


# def unpack_input_string(input_string) -> (list, dict, list):
#     """
#     Take the input template and unpack the args and kwargs if they exist.
#     Updates the command_args and command_kwargs with a list of strings and
#     list of dicts respectively.
#     """
#     if input_string is None:
#         print()
#         return
#
#
#     input_list = shlex.split(input_string)
#     # input_list = input_string.split()
#     input_list_length = len(input_list)
#     args = []
#     kwargs = {}
#     flags = []
#
#     i = 0
#     while i < input_list_length:
#
#         raw_arg = input_list[i]
#         if i + 1 < input_list_length:
#             next_raw_arg = input_list[i + 1]
#         else:
#             # Allows logic for if last item has `--` in it then it is a flag
#             next_raw_arg = "-"
#
#         if (raw_arg.startswith('--') or raw_arg.startswith('-')) and not next_raw_arg.startswith('-'):
#             # Field is a kwarg
#             kwargs.update({strip_dashes(raw_arg): input_list[i + 1]})
#             i += 1
#         elif (raw_arg.startswith('--') or raw_arg.startswith('-')) and next_raw_arg.startswith('-'):
#             # Field is a flag
#             flags.append(strip_dashes(raw_arg))
#         else:
#             # Field is an argument
#             args.append(strip_dashes(raw_arg))
#         i += 1
#
#     return args, kwargs, flags


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


def remove_hook_indicator_compact_expressions(context: 'Context'):
    if len(context.key_path) == 0:
        return
    if context.key_path[-1].startswith('<'):
        # For compact expressions we remove the leading angle bracket
        context.key_path[-1] = context.key_path[-1][1:]


def get_directory_sources(context: 'Context', first_arg):
    # Search in potential locations
    repository_candidates = [first_arg, os.path.join(settings.tackle_dir, first_arg)]

    if context.directory:
        repository_candidates = [
            os.path.join(s, context.directory) for s in repository_candidates
        ]

    for repo_candidate in repository_candidates:
        context.context_file = repository_has_tackle_file(
            repo_candidate, context.context_file
        )
        if not context.context_file:
            # Means that no valid context file has been found or provided
            continue
        else:
            context.repo_dir = Path(os.path.abspath(repo_candidate))
            context.template_name = os.path.basename(os.path.abspath(repo_candidate))
            context.tackle_gen = determine_tackle_generation(context.context_file)

            # Special exception for compact hook expressions
            remove_hook_indicator_compact_expressions(context)
            # TODO
            context.update_input_dict()
            walk_context(context=context)

            return

    raise RepositoryNotFound(
        'A valid repository for "{}" could not be found in the following '
        'locations:\n{}'.format(first_arg, '\n'.join(repository_candidates))
    )


def update_source(context: 'Context', global_context: bool = True):
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
    # from tackle.hooks import get_hook
    # x = context.get_hook(context.args[0])
    # if x:
    #     print()
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
            password=context.password,
        )
        repository_candidates = [unzipped_dir]
        context.cleanup = True
        # TODO: Fix this
        get_directory_sources(context, first_arg)  # TODO: This is wrong
    # Repo
    elif is_repo_url(first_arg):
        cloned_repo = clone(
            repo_url=first_arg,
            checkout=context.checkout,
            clone_to_dir=settings.provider_dir,
            no_input=context.no_input,
        )
        repository_candidates = [cloned_repo]
        # TODO: Fix this
        get_directory_sources(context, cloned_repo)  # TODO: This is wrong
    # File
    elif is_file(first_arg):
        # Special case where the input is a path to a file. Need to override some
        # settings that would normally get populated by zip / repo refs
        context.context_file = os.path.basename(first_arg)
        context.repo_dir = Path(first_arg).parent.absolute()
        context.template_name = os.path.basename(os.path.abspath(context.repo_dir))
        context.tackle_gen = determine_tackle_generation(context.context_file)

        update_global_args(context, args, kwargs, flags)

        # Special exception for compact hook expressions
        remove_hook_indicator_compact_expressions(context)

        # Entrypoint to main parsing logic
        context.update_input_dict()
        walk_context(context=context)
        return

    # elif is_template(first_arg):
    #     pass

    # Calling a hook directly
    elif get_hook(first_arg, context, suppress_error=True):
        """Main entrypoint to hook parsing logic. All hook calls are funneled here."""
        hook_value = nested_get(context.input_dict, context.key_path)

        remove_hook_indicator_compact_expressions(context)

        # if context.key_path[-1].startswith('<'):
        #     # For compact expressions we remove the leading angle bracket
        #     context.key_path[-1] = context.key_path[-1][1:]

        if isinstance(hook_value, dict):
            context.hook_dict = HookDict(**hook_value)
        else:
            context.hook_dict = HookDict()

        # context.hook_dict = HookDict(**nested_get(context.input_dict, context.key_path))

        context.hook_dict._args = args
        for k, v in kwargs.items():
            setattr(context.hook_dict, k, v)
        # context.hook_dict._kwargs = kwargs

        context.hook_dict._flags = flags

        # context.hook_dict = HookDict(**context.kwargs)
        context.hook_dict.hook_type = first_arg

        # from tackle.tackle import parse_hook
        # run_hook(context, hook_type=first_arg)
        parse_hook(context)
        # This is a special case where a hook is called either from the command line or
        # it is called in a compact call, ie in yaml `<a_key: print this -if stuff==things

        return

    from tackle.exceptions import UnknownHookTypeException

    # TODO: Raise better error
    raise UnknownHookTypeException

    # else:
    #     # Search in potential locations
    #     repository_candidates = [
    #         first_arg,
    #         os.path.join(settings.tackle_dir, first_arg),
    #     ]
    #
    # if first_arg == '.':
    #     print()
    #
    # if context.directory:
    #     repository_candidates = [
    #         os.path.join(s, context.directory) for s in repository_candidates
    #     ]
    #
    # for repo_candidate in repository_candidates:
    #     context.context_file = repository_has_tackle_file(
    #         repo_candidate, context.context_file
    #     )
    #     if not context.context_file:
    #         # Means that no valid context file has been found or provided
    #         continue
    #     else:
    #         context.repo_dir = Path(os.path.abspath(repo_candidate))
    #         context.template_name = os.path.basename(os.path.abspath(repo_candidate))
    #         context.tackle_gen = determine_tackle_generation(context.context_file)
    #
    #         # Special exception for compact hook expressions
    #         remove_hook_indicator_compact_expressions(context)
    #         # TODO
    #         context.update_input_dict()
    #         walk_context(context=context)
    #
    #         return
    #
    # raise RepositoryNotFound(
    #     'A valid repository for "{}" could not be found in the following '
    #     'locations:\n{}'.format(first_arg, '\n'.join(repository_candidates))
    # )


def raise_hook_validation_error(e, Hook, context: 'Context'):
    """Raise more clear of an error when pydantic fails to parse an object."""
    if 'extra fields not permitted' in e.__repr__():
        # Return all the fields in the hook by removing all the base fields.

        x = [i for i in Hook(input_string='tmp').dict().keys()]

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
        # fields = '--> ' + ', '.join(
        #     [
        #         i
        #         for i in Hook(input_string='tmp').dict().keys()
        #         if i not in BaseHook(input_string='tmp', type=context.hook_dict.hook_type).dict().keys() and i != 'type'
        #     ]
        # )
        error_out = (
            f"Error: The field \"{e.raw_errors[0]._loc}\" is not permitted in "
            f"file=\"{context.context_file}\" and key_path=\"{context.key_path}\".\n"
            f"Only values accepted are {fields}, (plus base fields --> "
            f"type, when, loop, chdir, merge)"
        )
        raise HookCallException(error_out)
    # elif 'value is not a valid' in e.__repr__():
    #     error_out = (
    #         f"Error: The \"{e.raw_errors[0]._loc}\" {e.raw_errors[0].exc} "
    #         f"when parsing file=\"{context.context_file}\" and key=\"{context.key}\"."
    #     )
    #     raise HookCallException(error_out)
    else:
        raise e


# def set_hook(hook_dict: 'Context', hook_arg_index: int, arg_schema):
def set_hook(context: 'Context', Hook: Type[BaseHook], index: int, value):
    # literal_type converts string to typed var
    if 'render_by_default' in Hook.__fields__[Hook._args[index]].field_info.extra:
        if Hook.__fields__[Hook._args[index]].field_info.extra['render_by_default']:
            value = render_variable(context, "{{" + value + "}}")
            setattr(context.hook_dict, Hook._args[index], value)
            return

    setattr(context.hook_dict, Hook._args[index], literal_type(value))


def evaluate_args(
    context: 'Context',
    Hook: Type[BaseHook],
):
    """
    Associate arguments provided in the call with hook attributes. Takes"""
    for i, v in enumerate(context.hook_dict._args):
        # Iterate over the input args
        if i + 1 == len(Hook._args):
            # We are at the last argument mapping so we need to join the remaining
            # arguments as a single string. Was parsed on spaces so reconstructed.
            # x = [Hook.__fields__[j] for j in Hook._args[i:]]
            # y = Hook.__fields__[Hook._args[i]]
            # z = Hook.__fields__[Hook._args[i]].type_
            if (
                isinstance(
                    Hook.__fields__[Hook._args[i]], (str, float, int, bool, bytes)
                )
                or Hook.__fields__[Hook._args[i]].type_ == Any
            ):
                value = ''.join(context.hook_dict._args[i:])
            elif isinstance(Hook.__fields__[Hook._args[i]], list):
                value = context.hook_dict._args[i:]

            else:
                if len(context.hook_dict._args[i:]) > 1:
                    raise ValueError(
                        f"Can't specify multiple arguments for map argument "
                        f"{Hook.__fields__[Hook._args[i]]}."
                    )
                value = context.hook_dict._args[i]
                # Join everything up as a list as it doesn't make sense to do anything
                # else at this point.
                # value = [Hook.__fields__[j] for j in Hook._args[i:]]
            set_hook(context, Hook, i, value)
            return
        else:
            # The hooks arguments are indexed
            set_hook(context, Hook, i, v)


def run_hook(context: 'Context', hook_type: str = None):
    """Get and call the hook."""
    Hook = get_hook(context.hook_dict.hook_type, context)

    # Arguments from call are assocaited with arguments in the hook
    evaluate_args(context, Hook)
    try:
        # Take the items out of the global context and mode if they are declared in the
        # hook dict. This establishes a precedence that attributes declared in the hook
        # are used when running the hook instead of items declared in the context.
        hook_exclude = {i for i in HookDict.__fields__}
        hook_exclude.update({'_args', '_kwargs', '_flags'})
        hook_context = context.hook_dict.dict(exclude=hook_exclude)
        context_exclude = {i for i in hook_context}
        context_exclude.add('env')
        hook = Hook(**hook_context, **context.dict(exclude=context_exclude))
        hook_output = hook.call()

        return hook_output

    # except ValidationError as e:
    #     raise_hook_validation_error(e, Hook, context)
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


def evaluate_loop(context: 'Context', output_dict: dict):
    """Run the parse_hook function in a loop and return a list of outputs."""
    loop_targets = render_variable(context, context.hook_dict.for_)
    # context.hook_dict.pop('loop')

    if len(loop_targets) == 0:
        # context.output_dict[context.key] = []
        return []

    reverse = False
    if 'reverse' in context.hook_dict:
        # Handle reverse boolean logic
        reverse = render_variable(context, context.hook_dict.reverse)
        if not isinstance(reverse, bool):  # TODO: pydantic validator
            raise HookCallException("Parameter `reverse` should be boolean.")
        # context.hook_dict.pop('reverse')

    loop_output = []
    for i, l in (
        enumerate(loop_targets)
        if not reverse
        else reversed(list(enumerate(loop_targets)))
    ):
        # Create temporary variables in the context to be used in the loop.
        # context.output_dict.update({'index': i, 'item': l})
        # output_dict.update({'index': i, 'item': l})
        context._index = i
        context._item = l
        loop_output += [parse_hook(context, append_key=True)]

    # # Remove temp variables
    # context.output_dict.pop('item')
    # context.output_dict.pop('index')
    # context.output_dict[context.key] = loop_output
    # return context.output_dict

    output_dict.pop('item')
    output_dict.pop('index')
    return loop_output
    # output_dict[context.key] = loop_output
    # return output_dict


def parse_hook(
    context: 'Context',
    output_dict: dict = None,
    append_key: bool = False,
):
    """Parse input dict for loop and when logic and calls hooks.

    :return: cc_dict
    """
    # TODO: RM?
    if output_dict is None:
        output_dict = {}

    logger.debug(
        "Parsing context_key: %s and key: %s" % (context.context_key, context.key_)
    )
    # context.hook_dict = context.input_dict[context.context_key][context.key]
    # context.hook_dict = context.value

    else_object = None
    if context.hook_dict.else_:
        else_object = render_variable(context, context.hook_dict.else_)
        # context.hook_dict.pop('else')

    if evaluate_if(context.hook_dict, context):
        # Extract for loop
        if context.hook_dict.for_:
            # This runs the current function in a loop and returns a list of results
            return evaluate_loop(context=context, output_dict=output_dict)

        # Block hooks are run independently. This prevents the rest of the hook dict from
        # being rendered ahead of execution.
        if context.hook_dict.hook_type != 'block':
            for k, v in context.hook_dict.dict().items():
                setattr(context.hook_dict, k, render_variable(context, v))
            # context.hook_dict = HookDict(**render_variable(context, context.hook_dict.dict()))
        if evaluate_confirm(context):
            return

        # Run the hook
        if context.hook_dict.merge:
            # Merging is for dict outputs only where the entire dict is inserted into the
            # output dictionary.
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
                nested_set(context.output_dict, context.key_path[1:] + [k], v)

        else:
            # Normal hook run
            # context.output_dict[context.key], post_gen_hook = run_hook(context)
            nested_set(context.output_dict, context.key_path, run_hook(context))
        # if post_gen_hook:
        #     # TODO: Update this per #4 hook-integration
        #     context.post_gen_hooks.append(post_gen_hook)

        if append_key:
            # TODO: ?
            return context.output_dict[context.key_]

    else:
        if else_object is not None:
            # Handle the false when condition if there is an `else` param.
            # if 'else' in context.hook_dict:
            if isinstance(else_object, dict):
                # If it is a dict, run it as another hook if type key exists, otherwise
                # fallback to dict
                if 'type' in else_object:
                    # context.input_dict[context.context_key][context.key] = else_object
                    nested_set(context.output_dict, context.key_path, else_object)
                    return parse_hook(context, append_key=append_key)

            else:
                # If list or str return tha actual value
                # context.output_dict[context.key] = render_variable(context, else_object)
                nested_set(
                    context.output_dict,
                    context.key_path,
                    render_variable(context, else_object),
                )

                return context.output_dict

    if context.hook_dict.callback:
        # Call a hook var but don't return it's output
        # TODO: RM?
        context.input_dict[context.context_key][
            context.key
        ] = context.hook_dict.callback
        return parse_hook(context, append_key=append_key)

    return context.output_dict


# Source: https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-context.input_dicttionary-given-a-list-of-indices-and-value
def walk_context(context: 'Context', parse_value: dict = None):
    if parse_value is None:
        parse_value = context.input_dict

    if (
        isinstance(parse_value, str)
        or isinstance(parse_value, int)
        or isinstance(parse_value, float)
    ):
        nested_set(context.output_dict, context.key_path, parse_value)

    elif isinstance(parse_value, dict):
        for i, (k, v) in enumerate(parse_value.items()):
            # context._index = i
            # from tackle.source1 import update_source

            if (k.startswith('<') or k.endswith('<')) and not k.endswith('>'):
                if len(k) <= 1:
                    context.input_string = v
                    update_source(context)
                    break
                # Compact expression handling means we need to override the key
                # path logic and handle loop independently
                context.key_path.append(k)
                context.key_ = k[1:]

                context.input_string = v
                update_source(context)
                context.key_path.pop()

            elif (
                isinstance(v, str)
                or isinstance(v, int)
                or isinstance(v, float)
                or v is None
            ):
                nested_set(context.output_dict, context.key_path + [k], v)
            elif v is None:
                context.key_path.append(k)
                # do something special
                context.key_path.pop()
            elif isinstance(v, list):
                context.key_path.append(k)
                for append_index, v_int in enumerate(v):
                    context.key_path.append([append_index])
                    walk_context(context, v_int)
                    context.key_path.pop()
                context.key_path.pop()
            elif isinstance(v, dict):
                context.key_path.append(k)
                walk_context(context, v)
                context.key_path.pop()
            else:
                print(
                    "###Type {} not recognized: {}.{}={}".format(
                        type(v), ".".join(context.key_path), k, v
                    )
                )


# Source: https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-context.input_dicttionary-given-a-list-of-indices-and-value
def walk_context_extract(context: 'Context', parse_value: dict = None):
    if parse_value is None:
        parse_value = context.input_dict

    if (
        isinstance(parse_value, str)
        or isinstance(parse_value, int)
        or isinstance(parse_value, float)
    ):
        nested_set(context.output_dict, context.key_path, parse_value)

    elif isinstance(parse_value, dict):
        for i, (k, v) in enumerate(parse_value.items()):
            # context._index = i
            # from tackle.source1 import update_source

            if (k.startswith('<') or k.endswith('<')) and not k.endswith('>'):
                if len(k) <= 1:
                    context.input_string = v
                    update_source(context)
                    break
                # Compact expression handling means we need to override the key
                # path logic and handle loop independently
                context.key_path.append(k)
                context.key_ = k[1:]

                context.input_string = v
                update_source(context)
                context.key_path.pop()

            elif (
                isinstance(v, str)
                or isinstance(v, int)
                or isinstance(v, float)
                or v is None
            ):
                nested_set(context.output_dict, context.key_path + [k], v)
            elif v is None:
                context.key_path.append(k)
                # do something special
                context.key_path.pop()
            elif isinstance(v, list):
                context.key_path.append(k)
                for append_index, v_int in enumerate(v):
                    context.key_path.append([append_index])
                    walk_context(context, v_int)
                    context.key_path.pop()
                context.key_path.pop()
            elif isinstance(v, dict):
                context.key_path.append(k)
                walk_context(context, v)
                context.key_path.pop()
            else:
                print(
                    "###Type {} not recognized: {}.{}={}".format(
                        type(v), ".".join(context.key_path), k, v
                    )
                )
