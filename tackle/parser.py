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
import os
import re
from pydantic import ValidationError
import logging
from ruyaml.constructor import CommentedKeyMap, CommentedMap

from typing import Any, Callable, Optional

from tackle import exceptions
from tackle.macros import run_macros
from tackle.models import (
    LazyBaseHook,
    LazyImportHook,
    Context,
    BaseHook,
    HookCallInput,
    CompiledHookType,
    AnyHookType,
    Hooks,
)
from tackle.hooks import create_declarative_hook
from tackle.hooks import get_hook
from tackle.render import render_variable
from tackle.utils.paths import work_in
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
    update_input_context,
    remove_arrows_from_key_path,
    cleanup_unquoted_strings,
)
from tackle.utils.command import unpack_args_kwargs_string
from tackle.utils.help import run_help
from tackle.utils.render import wrap_jinja_braces
from tackle.types import DocumentType, DocumentKeyType, DocumentValueType

logger = logging.getLogger(__name__)


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


def run_hook_in_dir(hook: CompiledHookType) -> Any:
    """Run the `exec` method in a dir is `chdir` is specified."""
    if hook.hook_call.chdir:
        path = os.path.abspath(os.path.expanduser(hook.hook_call.chdir))
        if os.path.isdir(path):
            # Use contextlib to switch dirs
            with work_in(os.path.abspath(os.path.expanduser(hook.hook_call.chdir))):
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
        Hook: CompiledHookType,
):
    """Render the hook variables."""
    render_exclude = Hook.model_fields['render_exclude'].default
    for k, v in hook_dict.items():
        if render_exclude and k in render_exclude:
            continue
        if k not in Hook.model_fields.keys():
            # If the hook has a `kwargs` field, then map it to that field.
            if Hook.model_fields['kwargs'].default is not None:
                default_kwargs = Hook.model_fields['kwargs'].default
                print(default_kwargs)
                if default_kwargs not in hook_dict:
                    hook_dict[default_kwargs] = {}
                hook_dict[default_kwargs][k] = render_variable(context, v)
                hook_dict.pop(k)
                continue

            # Get a list of possible fields for hook before raising error.
            possible_fields = [
                f"{key}: {value.annotation.__name__}"
                for key, value in Hook.model_fields.items()
                if key not in BaseHook.model_fields
            ]
            # TODO: Include link to docs -> Will need to also include provider name
            #  and then differentiate between lazy imported hooks which already have the
            #  provider and the ones that don't

            # TODO: Test with many types of Hooks - Lazy Function etc - I don't think
            #  they all will resolve
            provider_name = Hook.provider_name.title()
            base_url = "https://sudoblockio.github.io/tackle/providers"
            url = f"{base_url}/{provider_name}/{hook_type}/"
            raise exceptions.UnknownInputArgumentException(
                f"Key={k} not in hook={hook_dict['hook_type']}. Possible values are "
                f"{', '.join(possible_fields)}. \n\n See {url}"
                ,  # noqa
                context=context,
            ) from None

    for key, value in list(hook_dict.items()):
        if key not in Hook.model_fields.keys():
            # If the hook has a `kwargs` field, then map it to that field.
            if Hook.model_fields['kwargs'].default is not None:
                default_kwargs = Hook.model_fields['kwargs'].default
                print(default_kwargs)
                if default_kwargs not in hook_dict:
                    hook_dict[default_kwargs] = {}
                hook_dict[default_kwargs][key] = render_variable(context, value)
                hook_dict.pop(key)
                continue

            # Get a list of possible fields for hook before raising error.
            possible_fields = [
                f"{k}: {v.type_.__name__}"
                for k, v in Hook.model_fields.items()
                if k not in BaseHook.model_fields
            ]
            # TODO: Include link to docs -> Will need to also include provider name
            #  and then differentiate between lazy imported hooks which already have the
            #  provider and the ones that don't
            raise exceptions.UnknownInputArgumentException(
                f"Key={key} not in hook={hook_dict['hook_type']}. Possible values are "
                f"{', '.join(possible_fields)}",
                context=context,
            ) from None

        # if key in Hook.Config.alias_to_fields:
        #     # Skip any keys used in logic as these are evaluated / rendered separately
        #     continue

        # if key in Hook.model_fields['render_exclude'].default:
        #     # Skip anything that has been marked excluded. Needed for things like block
        #     # hooks which will have templating within the inputs
        #     continue

        if isinstance(value, str):
            # Check Hook private vars for rendering by default which wraps bare strings
            if Hook.model_fields['render_by_default'].default is not None \
                    and key in Hook.model_fields['render_by_default'].default:
                hook_dict[key] = render_variable(context, wrap_jinja_braces(value))

            # TODO: When we build our own custom Field function then this will change
            # TODO: This causes errors when the field is aliased as the lookup doesn't
            #  work and needs a deeper introspection.
            #  https://github.com/sudoblockio/tackle/issues/80
            #  Fixing with custom Field def should fix this.
            elif 'render_by_default' in Hook.model_fields[key].metadata_lookup:
                hook_dict[key] = render_variable(context, wrap_jinja_braces(value))

            elif ('{{' in value and '}}' in value) or ('{%' in value and '%}'):
                hook_dict[key] = render_variable(context, value)

        elif isinstance(value, (list, dict)):
            hook_dict[key] = render_variable(context, value)


def parse_sub_context(
        context: 'Context',
        hook_call: HookCallInput,
        target: str,
):
    """
    Reparse a subcontext as in the case with `else` and `except` where you have to
     handle the negative side of the either `if` or `try`. Works on both looped and
     normal runs by checking the last item in the key path. Then overwrites the input
     with a new context.
    """
    hook_target = getattr(hook_call, target)

    if isinstance(hook_target, str):
        set_key(
            context=context,
            value=render_variable(context, hook_call[target]),
        )
        return
    elif isinstance(hook_target, (bool, int, float)):
        set_key(
            context=context,
            value=hook_target,
        )
        return

    indexed_key_path = context.key_path[
                       (len(context.key_path_block) - len(context.key_path)):  # noqa
                       ]

    if isinstance(indexed_key_path[-1], bytes):
        # We are in a for loop
        input_dict = nested_get(
            element=context.input_context,
            keys=indexed_key_path[:-3],
        )
        updated_item = [
            hook_call[target] if i == decode_list_index(context.key_path[-1]) else None
            for i in range(decode_list_index(context.key_path[-1]) + 1)
        ]
        # TODO: Figure out wtf is going on here...
        input_dict[indexed_key_path[-3]] = updated_item
        walk_document(
            context,
            value=input_dict[indexed_key_path[-3]][
                decode_list_index(context.key_path[-1])
            ],
        )

    else:
        input_dict = nested_get(
            element=context.input_context,
            keys=indexed_key_path[:-2],
        )
        arrow = context.key_path[-1]
        input_dict[indexed_key_path[-2]] = {arrow: 'block', 'items': hook_call[target]}
        walk_document(context, value=input_dict[indexed_key_path[-2]])


def new_hook(
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
):
    """Create a new instantiated hook."""
    # TODO: WIP - https://github.com/sudoblockio/tackle/issues/104
    # Both no_input and skip_output can be used in both the hook call and hook
    # definition.
    no_input = Hook.model_fields['skip_output'].default | hook_call.no_input | context.no_input  # noqa
    skip_output = Hook.model_fields['skip_output'].default | hook_call.skip_output
    try:
        hook = Hook(
            context=context,
            hook_call=hook_call,
            no_input=no_input,
            skip_output=skip_output,
            **hook_call.hook_dict,
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
        if 'try' in hook_call and hook_call['try']:
            if 'except' in hook_call and hook_call['except']:
                parse_sub_context(context=context, hook_call=hook_call, target='except')
            return

        msg = str(e)
        if Hook.identifier.startswith('tackle.providers'):
            id_list = Hook.identifier.split('.')
            provider_doc_url_str = id_list[2].title()
            # Replace the validated object name (ex PrintHook) with the
            # hook_type field that users would more easily know.
            msg = msg.replace(id_list[-1], f"{hook_call['hook_type']} hook")

            msg += (
                f"\n Check the docs for more information on the hook -> "
                f"https://sudoblockio.github.io/tackle/providers/"
                f"{provider_doc_url_str}/{hook_call['hook_type']}/"
            )
        raise exceptions.HookParseException(str(msg), context=context) from None
    return hook


def update_hook_with_kwargs_field(
        *,
        context: 'Context',
        hook_dict: dict,
        kwargs: dict,
):
    """
    In order to facilitate instantiating objects with dicts, a `kwargs` key can be used
     to load the object. For instance `->: a_hook --kwargs a_dict`
    """
    if isinstance(kwargs, dict):
        hook_dict.update(kwargs)
    elif isinstance(kwargs, str):
        try:
            hook_dict.update(
                render_variable(
                    context=context,
                    raw=wrap_jinja_braces(kwargs),
                )
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
        hook_call: HookCallInput,
        Hook: CompiledHookType,
        append_hook_value: bool = None,
):
    """Parse the remaining arguments such as try/except and merge"""
    # Parse `kwargs` field which is a dict that will map to hook fields
    if hook_call.kwargs is not None:
        update_hook_with_kwargs_field(
            context=context,
            hook_dict=hook_call.hook_dict,
            kwargs=hook_call.kwargs,
        )

    if Hook.model_fields['kwargs'].default:
        # Need to map additional args to
        hook_call.hook_dict[Hook.model_fields['kwargs'].default].update()

    # Render the remaining hook variables
    render_hook_vars(
        context=context,
        hook_dict=hook_call.hook_dict,
        Hook=Hook,
    )

    # Instantiate the hook
    hook = new_hook(
        context=context,
        hook_call=hook_call,
        Hook=Hook,
    )
    if hook is None:
        return

    # Main exec logic
    if hook_call.try_:
        try:
            hook_output_value = run_hook_in_dir(hook=hook)
        except Exception as e:
            logger.debug("")
            if hook_call.except_:
                parse_sub_context(
                    context=context,
                    hook_call=hook_call.except_,
                    target='except',
                )
            return
    else:
        # Normal hook run
        hook_output_value = run_hook_in_dir(hook)

    if hook.skip_output:
        # hook property that is only true for `block`/`match` hooks which write to the
        # contexts themselves, thus their output is normally skipped except for merges.
        if hook_call.merge:
            # In this case we take the public context and overwrite the current context
            # with the output indexed back one key.
            merge_block_output(
                hook_output_value=hook_output_value,
                context=context,
                append_hook_value=append_hook_value,
            )
        elif context.data.temporary is not None:
            # Write the indexed output to the `temporary_context` as it was only written
            # to the `public_context` and not maintained between items in a list
            if not isinstance(context.key_path[-1], bytes):
                get_set_temporary_context(context)

    elif hook_call.merge:
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


def evaluate_for(
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
):
    """Run the parse_hook function in a loop with temporary variables."""
    if isinstance(hook_call.for_, str):
        for_split = hook_call.for_.split(' in ')
        if len(for_split) == 1:
            # Render first variable which should be a list or dict
            loop_targets = render_variable(
                context=context,
                raw=wrap_jinja_braces(hook_call.for_),
            )
            # Assume the names as we don't have any other context
            # TODO: Support lists of default variables names? ie i, v + k, v
            index_name = 'index'
            if isinstance(loop_targets, list):
                key_name = None
                value_name = 'item'
            else:
                key_name = 'key'
                value_name = 'value'

        elif len(for_split) == 2:
            # Render second variable which should be a list or dict
            loop_targets = render_variable(
                context=context,
                raw=wrap_jinja_braces(for_split[1]),
            )
            names_split = [i.strip() for i in for_split[0].split(',')]
            if len(names_split) == 1:
                index_name = 'index'
                key_name = 'key'
                value_name = names_split[0]
            elif len(names_split) == 2:
                index_name = 'index'
                key_name = names_split[0]
                value_name = names_split[1]
            else:
                raise exceptions.MalformedTemplateVariableException
        else:
            raise exceptions.MalformedTemplateVariableException
    else:
        index_name = 'index'
        value_name = 'item'
        loop_targets = hook_call.for_

    if not isinstance(loop_targets, (list, dict)):
        raise exceptions.MalformedTemplateVariableException(
            f"The `for` field must be a list or string reference to a list. The value "
            f"is of type `{type(loop_targets).__name__}`.", context=context,
        ) from None
    if len(loop_targets) == 0:
        return

    if isinstance(loop_targets, list):
        if hook_call.merge:
            set_key(context=context, value=[])
        elif not hook_call['merge']:
            set_key(context=context, value=[])
        for i, l in (
                enumerate(loop_targets)
                if not render_variable(context, hook_call.get('reverse', None))
                else reversed(list(enumerate(loop_targets)))
        ):
            # Create temporary variables in the context to be used in the loop.
            context.existing_context.update({index_name: i, value_name: l})
            # Append the index to the keypath
            context.key_path.append(encode_list_index(i))
            # Reparse the hook with the new temp vars in place
            parse_hook(
                context=context,
                hook_call=hook_call.copy(),
                Hook=Hook,
                append_hook_value=True,
            )
            context.key_path.pop()

    elif isinstance(loop_targets, dict):
        if hook_call.merge:
            set_key(context=context, value={})
        elif not hook_call.merge:
            set_key(context=context, value={})
        for i, l in (
                enumerate(loop_targets.items())
                if not render_variable(context, hook_call.get('reverse', None))
                else reversed(list(enumerate(loop_targets)))
        ):
            # Create temporary variables in the context to be used in the loop.
            context.existing_context.update({index_name: i, value_name: l})
            # Append the index to the keypath
            context.key_path.append(encode_list_index(i))
            # Reparse the hook with the new temp vars in place
            parse_hook(
                context=context,
                hook_call=hook_call.copy(),
                Hook=Hook,
                append_hook_value=True,
            )
            context.key_path.pop()
    else:
        raise Exception("Should never happen...")

    # Remove temp variables
    try:
        context.existing_context.pop(value_name)
        context.existing_context.pop(index_name)
    except KeyError:
        pass


def parse_hook_loop(
        *,
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
        append_hook_value: bool = None,
):
    if hook_call.for_:
        # This runs the current function in a loop with `append_hook_value` set so
        # that keys are appended in the loop.
        evaluate_for(context=context, hook_call=hook_call, Hook=Hook)
    else:
        parse_hook_execute(
            context=context,
            hook_call=hook_call,
            Hook=Hook,
            append_hook_value=append_hook_value,
        )


def evaluate_if(
        *,
        context: 'Context',
        hook_call: HookCallInput,
        append_hook_value: bool,
) -> bool:
    """Evaluate the if/when condition and return bool."""

    def raise_if_not_bool(return_value: Any, method: str):
        if isinstance(return_value, bool):
            return return_value
        raise exceptions.UnknownInputArgumentException(
            f"The result of evaluating method='{method}' resulted in the value="
            f"'{return_value}' and is not a boolean. Exiting...", context=context
        ) from None

    if hook_call.when is not None:
        return raise_if_not_bool(
            return_value=render_variable(context, wrap_jinja_braces(hook_call.when)),
            method='when'
        )
    elif hook_call.for_ is not None and not append_hook_value:
        # We qualify `if` conditions within for loop logic
        return True
    elif hook_call.if_ is None:
        return True
    else:
        return raise_if_not_bool(
            return_value=render_variable(context, wrap_jinja_braces(hook_call.if_)),
            method='if'
        )


def parse_hook(
        *,
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
        append_hook_value: bool = None,
):
    """Parse input dict for loop and when logic and calls hooks."""
    if evaluate_if(
            context=context,
            hook_call=hook_call,
            append_hook_value=append_hook_value,
    ):
        parse_hook_loop(
            context=context,
            hook_call=hook_call,
            Hook=Hook,
            append_hook_value=append_hook_value,
        )
    elif hook_call.else_:
        parse_sub_context(
            context=context,
            hook_call=hook_call.else_,
            target='else',
        )


def evaluate_args(
        *,
        context: 'Context',
        args: list,
        hook_dict: dict,
        Hook: CompiledHookType,
):
    """
    Associate hook arguments provided in the call with hook fields and insert those
     values into the hook_dict which will be validated later. Does this by iterating
     over the args and associating them with the hook's `args` field, a list of string
     field names, attempting the respect the type of the field.

     For hooks with the last arg a string, it will join the remaining args with a space.
     For hooks with the last arg a list, it will insert values as a list.

     TODO: Fix for all cases args of type list then string - ie a lookahead
    """
    # Flag to inform if we are at end of args and need to pop the rest
    pop_all: bool = False

    hook_args: list = Hook.model_fields['args'].default
    for i, v in enumerate(args):
        # Iterate over the input args
        if i == len(hook_args) - 1:
            # We are at the last argument mapping so we need to join the remaining
            # arguments as a single string if it is not a list of another map.
            if not isinstance(args[i], (str, float)):
                # Catch list dict and ints - strings floats and bytes caught later
                value = args[i]
            elif Hook.model_fields[hook_args[i]].annotation == str:
                # Was parsed on spaces so reconstructed.
                value = ' '.join(args[i:])
                pop_all = True
            elif Hook.model_fields[hook_args[i]].annotation in (bool, float, int):
                # TODO: Incomplete
                value = args[i]
            elif Hook.model_fields[hook_args[i]].annotation == list:
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
                        f"{Hook.model_fields[hook_args[i]].default}.",
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


def run_hook_at_key_path(
        *,
        context: 'Context',
        hook_dict: dict,
        hook_str: str,
):
    """
    Run the hook by qualifying the input argument and matching the input params with the
     hook's `_args` which are then overlayed into a hook kwargs. Also interprets
     special cases where you have a string or list input of renderable variables.
    """
    args, kwargs, flags = unpack_args_kwargs_string(input_string=hook_str)
    # Look up the hook from the imported providers
    first_arg = args.pop(0)
    Hook = get_hook(
        context=context,
        hook_type=first_arg,
        args=args,
        kwargs=kwargs,
    )
    if Hook is None:
        exceptions.raise_unknown_hook(context=context, hook_type=first_arg)

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
    evaluate_args(
        args=args,
        hook_dict=hook_dict,
        Hook=Hook,
        context=context,
    )
    # Add any kwargs
    for k, v in kwargs.items():
        hook_dict[k] = v
    for i in flags:
        hook_dict[i] = True

    try:
        hook_call = HookCallInput(**hook_dict)
    except ValidationError as e:
        raise exceptions.UnknownInputArgumentException(
            e.__str__(), context=context,
        ) from None

    # Main parser
    parse_hook(
        context=context,
        hook_call=hook_call,
        Hook=Hook,
    )


def walk_document(context: 'Context', value: DocumentValueType):
    """
    Traverse an object looking for hook calls and running those hooks. Here we are
     keeping track of which keys are traversed in a list called `key_path` with strings
     as dict keys and byte encoded integers for list indexes.
    """
    if len(context.key_path) != 0:
        value = run_macros(context=context, value=value)

    if isinstance(value, dict):
        # Handle expanded expressions - ie key:\n  ->: hook_type args
        if '->' in value.keys():
            # Public hook calls
            context.key_path.append('->')
            # context.input_string = value['->']
            run_hook_at_key_path(
                context=context,
                hook_dict=value,
                hook_str=value.pop('->'),
            )
            context.key_path.pop()
            return
        elif '_>' in value.keys():
            # Private hook calls
            context.key_path.append('_>')
            context.input_string = value['_>']
            run_hook_at_key_path(context=context, hook_dict=value)
            context.key_path.pop()
            return
        # elif value == {} and context.key_path:
        elif value == {}:
            set_key(context=context, value={})
            return

        for k, v in value.copy().items():

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
                # blocks_macro(context)
                context.key_path[-1] = k[:-2]
                value = nested_get(
                    element=context.input_context,
                    keys=context.key_path[
                         (len(context.key_path_block) - len(context.key_path)):
                         ],
                )
                # Finally check if the `items` key exists in the input_context.  If not
                #  then we have an empty hook which will cause an ambiguous
                #  ValidationError for missing field
                if 'items' not in value:
                    raise exceptions.EmptyBlockException(
                        "Empty block hook.", context=context
                    ) from None

                walk_document(context, value)
                context.key_path.pop()
            else:
                # Recurse
                walk_document(context, v)
                context.key_path.pop()
    # Non-hook calls recurse through inputs
    elif isinstance(value, list):
        # Handle empty lists
        if len(value) == 0:
            set_key(context=context, value=value)
        else:
            for i, v in enumerate(value.copy()):
                context.key_path.append(encode_list_index(i))
                walk_document(context, v)
                context.key_path.pop()
    else:
        set_key(context=context, value=value)


def get_hook_kwargs_from_input_kwargs(
        hook: CompiledHookType,
        kwargs: dict,
) -> dict:
    """
    For consuming kwargs / flags, once the hook has been identified when calling hooks
     via CLI actions, this function matches the kwargs / flags with the hook and returns
     any unused kwargs / flags for use in the outer context. Note that flags are kwargs
     as they have already been merged by now.
    """
    for k, v in kwargs.copy().items():
        if k in hook.model_fields:
            if hook.model_fields[k].annotation == bool:
                # Flags -> These are evaluated as the inverse of whatever is the default
                if hook.model_fields[k].default:  # ie -> True
                    hook.model_fields[k].default = False
                else:
                    hook.model_fields[k].default = True
            else:
                # Kwargs
                hook.model_fields[k].default = v
            hook.model_fields[k].required = False  # Otherwise will complain
            kwargs.pop(k)
    return kwargs


def run_declarative_hook(
        context: 'Context',
        hook: LazyBaseHook,
) -> Any:
    """
    Given a hook with args, find if the hook has methods and if it does not, apply the
     args to the hook based on the `args` field mapping. Calls the hook.
    """
    kwargs = get_hook_kwargs_from_input_kwargs(
        hook=hook,
        kwargs=context.input.kwargs,
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

    # if isinstance(hook, LazyBaseFunction):
    #     hook = create_function_model(
    #         context=context,
    #         # TODO
    #         func_name=context.input_string,
    #         func_dict=hook.function_dict.copy(),
    #     )

    # Handle args
    arg_dict = {}
    num_popped = 0
    for i, arg in enumerate(context.input.args.copy()):
        # For running hooks in tackle files (ie not in `hooks` dir), we run this logic
        # as the hook is already compiled.
        if arg in hook.model_fields and hook.model_fields[arg].type_ == Callable:
            # Consume the args
            context.input.args.pop(i - num_popped)
            num_popped += 1

            # Gather the function's dict so it can be compiled into a runnable hook
            func_dict = hook.model_fields[arg].default.input_raw.copy()

            # Add inheritance from base function fields
            for j in hook.model_fields['function_fields'].default:
                # Base method should not override child.
                if j not in func_dict:
                    func_dict[j] = hook.model_fields[j]

            hook = create_declarative_hook(
                context=context,
                hook_name=hook.model_fields[arg].name,
                hook_input_raw=func_dict,
            )
        elif isinstance(hook, LazyBaseHook) and (
                arg + '<-' in hook.input_raw or arg + '<_' in hook.input_raw
        ):
            # Consume the args
            context.input.args.pop(i - num_popped)
            num_popped += 1

            # Gather the function's dict so it can be compiled into a runnable hook
            if arg + '<-' in hook.input_raw:
                func_dict = hook.input_raw[arg + '<-']
            else:
                func_dict = hook.input_raw[arg + '<_']

            # Add inheritance from base function fields
            if hook.hook_fields is not None:
                for j in hook.hook_fields:
                    # Base method should not override child.
                    if j not in func_dict:
                        func_dict[j] = hook.input_raw[j]
            hook = create_declarative_hook(
                context=context,
                hook_name=arg,
                hook_input_raw=func_dict,
            )

        elif arg == 'help':
            # Exit 0
            run_help(context=context, hook=hook)

        elif hook.model_fields['args'].default == []:  # noqa
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
    if 'args' in hook.model_fields:
        evaluate_args(context.input.args, arg_dict, Hook=hook, context=context)

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
        context: 'Context',
        hook: CompiledHookType,
):
    """
    Raise an error if not all the args / kwargs / flags have been consumed which would
     mean the user supplied extra vars and should be yelled at.
    """
    # TODO: Refactor into own file

    msgs = []
    if len(context.input.args) != 0:
        msgs.append(f"args {', '.join(context.input.args)}")
    if len(context.input.kwargs) != 0:
        missing_kwargs = ', '.join(
            [f"{k}={v}" for k, v in context.input.kwargs.items()])
        msgs.append(f"kwargs {missing_kwargs}")
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
                f"Could not find source = {context.input.args[0]} or as key / hook in"
                f" parent tackle file.", context=context,
            ) from None


def parse_input_args_for_hooks(context: 'Context'):
    """
    Process input args/kwargs/flags based on if the args relate to the default hook or
     some public hook (usually declarative). Once the hook has been identified, the
     args/kwargs/flags are consumed and if there are any args left, an error is raised.
    """
    num_args = len(context.input.args)
    if num_args == 0:
        if context.hooks.default:  # Default hook (no args)
            # TODO: Replace with run_decla
            context.data.public = run_declarative_hook(
                context=context,
                hook=context.hooks.default,
            )
            try:
                context.data.public = context.hooks.default(
                    **context.input.kwargs
                ).exec()
            except ValidationError as e:
                raise exceptions.UnknownInputArgumentException(
                    e.__str__(), context=context
                ) from None
    elif num_args == 1 and \
            context.input.args[0] == 'help' and \
            context.hooks.default is not None:
        run_help(context=context, hook=context.hooks.default)
    elif num_args == 1 and context.input.args[0] == 'help':
        run_help(context=context)
    elif num_args != 0:  # With args
        # TODO: Refactor into own file
        # Prioritize public_hooks (ie non-default hook) because if the hook exists,
        # then we should consume the arg there instead of using the arg as an arg for
        # default hook because otherwise the public hook would be unreachable.
        if context.input.args[0] in context.hooks.public:
            # Search within the public hook for additional args that could be
            # interpreted as methods which always get priority over consuming the arg
            # as an arg within the hook itself.
            public_hook = context.input.args.pop(0)  # Consume arg
            context.data.public = run_declarative_hook(
                context=context,
                hook=context.hooks.public[public_hook],
            )
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                hook=context.hooks.public[public_hook],
            )
        elif context.hooks.default:
            context.data.public = run_declarative_hook(
                context=context,
                hook=context.hooks.default,
            )
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                hook=context.hooks.default,
            )
        else:
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                hook=context.hooks.default,  # This is None if it does not exist
            )
    else:
        # If there are no declarative hooks defined, use the kwargs to override values
        #  within the context.
        context.data.input = update_input_context(
            input_dict=context.data.input,
            update_dict=context.input.kwargs,
        )
        # Apply overrides
        context.data.input = update_input_context(
            input_dict=context.data.input,
            update_dict=context.data.overrides,
        )


def get_declarative_hooks(context: 'Context'):
    """
    Iterates through all the keys of the raw_input and creates the default, public, or
     private hooks lazily.
    """
    for k, v in context.data.hooks_input.items():
        function_name = k[:-2]
        arrow = k[-2:]
        dcl_hook = LazyBaseHook(
            input_raw=v,
            is_public=True if arrow == '<-' else False,
        )
        if function_name == "":
            # dcl_hook is the default hook
            context.hooks.default = dcl_hook
        elif arrow == '<-':  # public hook
            context.hooks.public[function_name] = dcl_hook
        elif arrow == '<_':  # private hook
            context.hooks.private[function_name] = dcl_hook
        else:
            raise Exception("This should never happen")


def split_input_data(context: 'Context'):
    """
    Split the raw_input from a tackle file into pre/post_input objects if the data is an
     object skipping if it is a list.

     pre_input - data before the last hook definition
     post_input - data after the last hook definition

     This allows us to import hooks so that they are available before the args/kwargs
     are used to evaluate them. See TODO [docs]
    """
    context.data.hooks_input = {}
    if isinstance(context.data.raw_input, dict):
        context.data.pre_input = {}
        context.data.post_input = {}

    elif isinstance(context.data.raw_input, list):
        # List inputs won't be helpful in the pre input data so ignoring
        context.data.pre_input = []
        context.data.post_input = context.data.raw_input
        # Dcl hooks can only be defined in objects, not lists unless there is some
        # good reason to support that. Nothing else to do here
        return
    else:
        raise Exception("This should never happen")

    # Left with dict that we will now split into pre input, dcl hooks, and post input
    pre_data_buffer = {}
    for k, v in context.data.raw_input.items():
        # Check if it has a left arrow (hook definition)
        if re.match(r'^[a-zA-Z0-9\_]*(<\-|<\_)$', k):  # noqa
            context.data.hooks_input.update({k: v})
            # Clear the buffer
            context.data.pre_input.update(pre_data_buffer)
            pre_data_buffer = {}
        else:
            pre_data_buffer.update({k: v})
    # All remaining data must be declared after the last hook so part of post_input
    context.data.post_input = pre_data_buffer


def parse_context(context: 'Context', call_hooks: bool = True):
    """
    Main entrypoint to parsing a context. Called without the hooks arg normally, with
     hooks arg when importing declarative hooks from provider.
    """
    # Split the input data so that the pre/post inputs are separated from the hooks
    split_input_data(context=context)
    # Parse the pre_input before qualifying the help for imports and other
    if context.data.pre_input:
        context.data.input = context.data.pre_input
        walk_document(context=context, value=context.data.pre_input)
    # Get the remaining declarative hooks out of the context
    get_declarative_hooks(context=context)
    if call_hooks:  # Run except on import
        # We give hooks on import and don't want to evaluate args then
        parse_input_args_for_hooks(context=context)  # Evaluate args for calling hooks
    # Parse the post_input after running hooks if any
    if context.data.post_input:
        context.data.input = context.data.post_input
        walk_document(context=context, value=context.data.post_input)
