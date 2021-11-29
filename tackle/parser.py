"""Main parsing module for walking down arbitrary data structures and executing hooks."""
from __future__ import print_function
import logging
from PyInquirer import prompt

from pathlib import Path
import os
import inspect
from typing import Type, Any

from tackle import BaseHook
from tackle.providers import import_with_fallback_install
from tackle.render import render_variable, wrap_jinja_braces
from tackle.utils.dicts import (
    nested_get,
    nested_delete,
    encode_list_index,
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
from tackle.models import Context, BaseHook
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


def update_provider_source(context: 'Context'):
    pass


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

    # No other options for if it is a remote source so input should be hook
    Hook = get_hook(first_arg, context, suppress_error=True)

    if Hook is None:
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

    # Handle render by default
    # for k, v in Hook.__fields__.items():
    #     if 'render_by_default' in v.field_info.extra:
    #         hook_dict[k] = "{{" + hook_dict[k] + "}}"

    # Render the input variables
    # for k, v in hook_dict.items():
    #     hook_dict[k] = render_variable(context, v)

    import time

    now = time.time()

    hook = Hook(
        **hook_dict,
        input_dict=context.input_dict,
        output_dict=context.output_dict,
        # context=context
    )

    after = time.time() - now
    output = parse_hook(hook, context)

    # set_key(
    #     element=context.output_dict,
    #     keys=context.key_path,
    #     value=output,
    #     keys_to_delete=context.remove_key_list,
    # )

    # print()

    # if isinstance(hook_value, dict):
    #     context.hook_dict = HookDict(**hook_value)
    # else:
    #     context.hook_dict = HookDict()

    # Calling a hook directly
    # elif get_hook(first_arg, context, suppress_error=True):
    #     """Main entrypoint to hook parsing logic. All hook calls are funneled here."""
    #
    #     if context.key_path[-1] in ('->', '_>'):
    #         hook_value = nested_get(context.input_dict, context.key_path[:-1])
    #
    #         # Need to replace these keys as for the time being (pydantic 1.8.2) -
    #         # multiple aliases can't be specified so doing this hack
    #         if '->' in hook_value:
    #             hook_value['hook_type'] = hook_value['->']
    #             hook_value.pop('->')
    #         else:
    #             hook_value['hook_type'] = hook_value['_>']
    #             hook_value.pop('_>')
    #     else:
    #         hook_value = nested_get(context.input_dict, context.key_path)
    #
    #     if isinstance(hook_value, dict):
    #         context.hook_dict = HookDict(**hook_value)
    #     else:
    #         context.hook_dict = HookDict()
    #
    #     # Set the args which will be overlayed with the `evaluate_args` function later
    #     # that will override various parameters set within `_args` in the hook def.
    #     context.hook_dict._args = args
    #     # Set any kwars from the hook call - ie `->: somehook --if 'key.a_value == 2'`
    #     for k, v in kwargs.items():
    #         setattr(context.hook_dict, k, v)
    #
    #     # Set the hook_type
    #     context.hook_dict.hook_type = first_arg
    #
    #     # Parse for any loops / conditionals
    #     parse_hook(context)
    #     return
    #
    # from tackle.exceptions import UnknownHookTypeException
    #
    # # TODO: Raise better error
    # raise UnknownHookTypeException


# def raise_hook_validation_error(e, Hook, context: 'Context'):
#     """Raise more clear of an error when pydantic fails to parse an object."""
#     if 'extra fields not permitted' in e.__repr__():
#         # Return all the fields in the hook by removing all the base fields.
#         context_base_keys = (
#             BaseHook(input_string='tmp', type=context.hook_dict.hook_type).dict().keys()
#         )
#
#         fields = '--> ' + ', '.join(
#             [
#                 i
#                 for i in Hook(input_string='tmp').dict().keys()
#                 if i not in context_base_keys and i != 'type'
#             ]
#         )
#         error_out = (
#             f"Error: The field \"{e.raw_errors[0]._loc}\" is not permitted in "
#             f"file=\"{context.context_file}\" and key_path=\"{context.key_path}\".\n"
#             f"Only values accepted are {fields}, (plus base fields --> "
#             f"type, when, loop, chdir, merge)"
#         )
#         raise HookCallException(error_out)
#     else:
#         raise e


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
            # Was parsed on spaces so reconstructed.
            x = Hook.__fields__[Hook._args[i]]
            if Hook.__fields__[Hook._args[i]].type_ in (
                str,
                float,
                int,
                bool,
                bytes,
                Any,
            ):

                # if (
                #         isinstance(
                #             Hook.__fields__[Hook._args[i]], (str, float, int, bool, bytes)
                #         )
                #         or Hook.__fields__[Hook._args[i]].type_ == Any
                # ):
                value = ''.join(args[i:])
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
            # hook_dict[Hook._args[i]] = literal_type(value)
            # set_hook(hook_dict, Hook, i, value)
            return
        else:
            # The hooks arguments are indexed
            hook_dict[Hook._args[i]] = v
            # set_hook(hook_dict, Hook, i, v)
            return


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

    output = []
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
        output = parse_hook(hook.copy(), context, append_hook_value=True)

        context.key_path.pop()

        # set_key(
        #     element=context.output_dict,
        #     keys=context.key_path,
        #     value=output,
        #     keys_to_delete=context.remove_key_list,
        # )

    # Remove temp variables
    context.output_dict.pop('item')
    context.output_dict.pop('index')

    return output


def evaluate_if(hook: BaseHook, context: 'Context', append_hook_value: bool) -> bool:
    """Evaluate the when condition and return bool."""
    if hook.for_ is not None and not append_hook_value:
        return True
    if hook.if_ is None:
        return True
    return render_variable(context, hook.if_)


def render_hook_vars(hook: BaseHook, context: 'Context'):
    print()
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
            # This runs the current function in a loop and returns a list of results
            output = evaluate_for(hook, context)
            return output

        else:
            # Normal hook run
            render_hook_vars(hook, context)
            hook_output_value = hook.call()
            # return hook_output_value
            set_key(
                element=context.output_dict,
                keys=context.key_path,
                value=hook_output_value,
                keys_to_delete=context.remove_key_list,
                append_hook_value=append_hook_value,
            )

    elif hook.else_ is not None:
        print()

    else:
        # False side of the `if` condition
        if not append_hook_value:
            # Only delete the key if we're not in a loop where the key would not exist
            nested_delete(
                element=context.output_dict,
                keys=context.key_path,
            )


# context.key_path.pop()
# if post_gen_hook:
#     # TODO: Update this per #4 hook-integration
#     context.post_gen_hooks.append(post_gen_hook)

# if append_key:
#     # TODO: ?
#     return context.output_dict[context.key_]
#     if append_index:
#         # Case where we are in a loop and we are appending the output
#         set_key(
#             element=context.output_dict,
#             keys=context.key_path + [append_index],
#             value=hook_output_value,
#             keys_to_delete=context.remove_key_list,
#         )
#     else:

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

# return context.output_dict


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
