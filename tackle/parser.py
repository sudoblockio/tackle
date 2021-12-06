"""Main parsing module for walking down arbitrary data structures and executing hooks."""
from __future__ import print_function
import logging
from pathlib import Path
import os
import inspect
import re
import copy
from typing import Type, Any

from tackle.providers import import_with_fallback_install
from tackle.render import render_variable, wrap_jinja_braces
from tackle.utils.dicts import nested_get, nested_delete, encode_list_index, set_key
from tackle.utils.command import unpack_args_kwargs_string
from tackle.utils.vcs import get_repo_source
from tackle.utils.files import read_config_file
from tackle.utils.paths import is_repo_url, is_file, find_tackle_file
from tackle.utils.zipfile import unzip
from tackle.models import Context, BaseHook
from tackle.exceptions import UnknownHookTypeException, UnknownSourceException
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


# def update_global_args(context: 'Context', args: list, kwargs: dict, flags: list):
#     """
#     Handler for global args, kwargs, and flags when the source is one of zip, repo, or
#     directory. Both kwargs and flags update the override dictionary. Args are first
#     used to search within the `input_dict` to see if there is a key of that type and
#     jumping to that level and then using those arguments inside that hook call.
#     """
#     # context.global_kwargs = kwargs
#     # context.global_flags = flags
#     for k, v in kwargs:
#         context.override_inputs.update({k: v})
#
#     for i in flags:
#         context.override_inputs.update({i: True})
#
#     # TODO: Implement key seeking logic
#     # context.global_args = args


# def evaluate_merge(key_path: list, merge: bool):
#
#     if merge:
#         if key_path[-1] in ('->', '_>'):
#             pass
#         elif key_path[-1].endswith(('->', '_>')):
#             pass
#     else:
#         return key_path


def evaluate_for(hook: BaseHook, context: 'Context'):
    """Run the parse_hook function in a loop and return a list of outputs."""
    loop_targets = render_variable(context, hook.for_)
    hook.for_ = None

    # Need add an empty list in the value so we have something to append to
    set_key(
        element=context.output_dict,
        keys=context.key_path,
        value=[],
        keys_to_delete=context.remove_key_list,
    )

    if len(loop_targets) == 0:
        return

    for i, l in (
        enumerate(loop_targets)
        if not render_variable(context, hook.reverse)
        else reversed(list(enumerate(loop_targets)))
    ):
        # Create temporary variables in the context to be used in the loop.
        # TODO: Consider putting this in another dictionary that is looked up based
        #  on inspecting the raw template for refs.
        context.output_dict.update({'index': i, 'item': l})
        context.key_path.append(encode_list_index(i))

        # We need to parse a copy of the hook as
        # output.append(parse_hook(hook.copy(), context, append_hook_value=True))
        parse_hook(hook.copy(), context, append_hook_value=True)
        context.key_path.pop()

    # Remove temp variables
    context.output_dict.pop('item')
    context.output_dict.pop('index')

    # return output


def evaluate_if(hook: BaseHook, context: 'Context', append_hook_value: bool) -> bool:
    """Evaluate the when condition and return bool."""
    if hook.for_ is not None and not append_hook_value:
        return True
    if hook.if_ is None:
        return True
    return render_variable(context, hook.if_)


def render_hook_vars(hook: BaseHook, context: 'Context'):
    """Render the hook variables."""
    for k, v in hook.__fields__.items():
        hook_value = getattr(hook, k)

        if hook_value is None:
            continue

        if k in hook._render_exclude:
            continue

        if 'render_by_default' in v.field_info.extra:
            hook_value = wrap_jinja_braces(hook_value)

        setattr(hook, k, render_variable(context, hook_value))


def parse_hook(hook: BaseHook, context: 'Context', append_hook_value: bool = None):
    """Parse input dict for loop and when logic and calls hooks."""
    if evaluate_if(hook, context, append_hook_value):
        if hook.for_ is not None:
            # This runs the current function in a loop with `append_hook_value` set so
            # that keys are appended in the loop.
            evaluate_for(hook, context)
            return

        # if hook.while_ is not None:
        #     evaluate_when(hook, context)
        #     return

        else:
            # Normal hook run
            render_hook_vars(hook, context)
            hook_output_value = hook.call()
            set_key(
                element=context.output_dict,
                keys=context.key_path if not hook.merge else context.key_path[:-1],
                value=hook_output_value,
                keys_to_delete=context.remove_key_list,
                append_hook_value=append_hook_value,
            )
            return

    elif hook.else_ is not None:
        # TODO: Implement
        raise NotImplementedError

    # elif hook.match_ is not None:

    else:
        # False side of the `if` condition
        if not append_hook_value:
            # Only delete the key if we're not in a loop where the key would not exist
            nested_delete(
                element=context.output_dict,
                keys=context.key_path,
            )


def is_tackle_hook(value):
    """Regex qualify if the key is a hook."""
    if isinstance(value, bytes):
        return False

    REGEX = re.compile(
        r"""^.*(->|_>)$""",
        re.VERBOSE,
    )
    return bool(REGEX.match(value))


def run_hook_function(context: 'Context'):
    """
    Run either a hook or a function. In this context the args are associated with
    arguments in
    """
    args, kwargs, flags = unpack_args_kwargs_string(context.input_string)
    first_arg = args[0]
    # Remove first args it will be consumed and no longer relevant
    args.pop(0)

    if '{{' in first_arg and '}}' in first_arg:
        args.append(first_arg)
        first_arg = 'var'

    # Look up the hook from the imported providers
    Hook = get_hook(first_arg, context, suppress_error=True)

    if Hook is None:
        # TODO: Rm and raise error in get_hook?
        from tackle.exceptions import UnknownHookTypeException

        raise UnknownHookTypeException

    if context.key_path[-1] in ('->', '_>'):
        # We have a expanded or mixed (with args) hook expression and so there will be
        # additional properties in adjacent keys
        hook_dict = nested_get(context.input_dict, context.key_path[:-1])

        # Need to replace arrow keys as for the time being (pydantic 1.8.2) - multiple
        # aliases for the same field (type) can't be specified so doing this hack
        if '->' in hook_dict:
            hook_dict['type'] = hook_dict['->']
            hook_dict.pop('->')
        else:
            hook_dict['type'] = hook_dict['_>']
            hook_dict.pop('_>')
    else:
        # Hook is a compact expression - Can only be a string
        hook_dict = {}
        # hook_dict['type'] = nested_get(context.input_dict, context.key_path)
        hook_dict['type'] = first_arg

    # Associate hook arguments provided in the call with hook attributes
    evaluate_args(args, hook_dict, Hook)
    # Add any kwargs
    for k, v in kwargs.items():
        hook_dict[k] = v

    hook = Hook(
        **hook_dict,
        input_dict=context.input_dict,
        output_dict=context.output_dict,
        no_input=context.no_input,
    )

    # Main parser
    parse_hook(hook, context)


def walk_sync(context: 'Context', element):
    """Traverse an object looking for hook calls."""
    if isinstance(element, str):
        if is_tackle_hook(context.key_path[-1]):  # Regex qualify
            if len(context.key_path[-1]) == 2:
                # Expanded or mixed expression - ie in ('->', '_>')
                context.input_string = element
                run_hook_function(context)
                return
            # Compact expression
            context.input_string = element
            run_hook_function(context)
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

    return context.output_dict


def get_base_file(context: 'Context'):
    """Read the tackle file and copy it's contents into the output_dict."""
    context.input_dict = read_config_file(
        os.path.join(context.repo_dir, context.context_file)
    )
    context.output_dict = copy.deepcopy(context.input_dict)


def import_local_provider_source(context: 'Context', provider_dir: str):
    """
    Import a provider from a path by checking if the provider has a tackle file and
    returning a path.
    """
    context.repo_dir = provider_dir
    if context.context_file is None:
        context.context_file = find_tackle_file(provider_dir)

    if context.directory_:
        context.context_file = os.path.join(context.context_file, context.directory_)

    get_base_file(context)


def evaluate_args(args: list, hook_dict: dict, Hook: Type[BaseHook]):
    """
    Associate hook arguments provided in the call with hook attributes. Parses the
    hook's `_args` attribute to know how to map arguments are mapped to where and
    deal with rendering by default.
    """
    for i, v in enumerate(args):
        # Iterate over the input args
        if i + 1 == len(Hook._args):
            # We are at the last argument mapping so we need to join the remaining
            # arguments as a single string if it is not a list of another map.
            if Hook.__fields__[Hook._args[i]].type_ in (str, float, int, bool, Any):
                # Was parsed on spaces so reconstructed.
                value = ' '.join(args[i:])
            # fmt: skip
            elif isinstance(Hook.__fields__[Hook._args[i]], list):
                # If list then all the remaining items
                value = args[i:]
            else:
                # Only thing left is a dict
                if len(args[i:]) > 1:
                    raise ValueError(
                        f"Can't specify multiple arguments for map argument "
                        f"{Hook.__fields__[Hook._args[i]]}."
                    )
                # Join everything up as a list as it doesn't make sense to do anything
                # else at this point.
                value = args[i]

            hook_dict[Hook._args[i]] = value
            return
        else:
            # The hooks arguments are indexed
            hook_dict[Hook._args[i]] = v


def update_source(context: 'Context'):
    """
    Locate the repository directory from a template reference. This is the main parser
    for determining the source of the context and calls the succeeding parsing
    functions. The parsing order has the following order of precedence.

    If the template wasn't given then use the file in that parent directory.
    If the template refers to a zip file or zip url, download / unzip as the context.
    If the template refers to a repository URL, clone it.
    If the template refers to a file, use that as the context.
    If the template refers to a hook, run that hook with arguments inserted.
    If the template is a path to a local repository, use it.
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
            password=context.password_,  # TODO: RM - Should prompt?
        )
        import_local_provider_source(context, unzipped_dir)
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
    else:
        # TODO: Improve
        raise UnknownSourceException
