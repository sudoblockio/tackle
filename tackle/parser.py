"""
Core parser for tackle. It does the following steps

- Reads in a tackle provider and loads its input data / hooks
  - Splits the data into two sections pre / post input sections
  - Pre-input data is all the data before the last hook is declared
  - Between the pre-input and post input, all hooks are read
- Parses the pre-input section first before any external args / kwargs supplied via
command line are asserted
  - This allows a tackle file to have imports that have other hooks so that external
  args like `help` can be run with all the hooks available
    - Otherwise running `help` etc would need to parse the whole document
- Iterate through any keys on the input data
  - Perform macros to expand keys so that they are more easily read by business logic
  - Copy input values over to a output data split between public, private, temporary and
  existing memory spaces. Only public is passed between contexts - see memory management
  docs
- Run any hooks
  - Perform any logic (if / else / for etc)
  - Call the actual hook
  - Insert the output into the appropriate key in the appropriate memory space

This is a really rough overview of what is going on here. Post issues if you are trying
to fix something and want to know more. Docs should be improved always...
"""
import inspect
from collections import OrderedDict
import os
import re
import logging
from pydantic import ValidationError, BaseModel
from typing import Any, Callable

from tackle import exceptions
from tackle.macros.key_macros import (
    var_hook_macro,
    key_macro,
    unquoted_yaml_template_macro,
)
from tackle.models import (
    LazyBaseHook,
    HookCallInput,
    CompiledHookType,
)
from tackle.context import Context
from tackle.hooks import create_dcl_hook, get_hook
from tackle.render import render_variable
from tackle.types import DocumentValueType
from tackle.utils.paths import work_in
from tackle.utils.dicts import (
    get_set_temporary_context,
    get_target_and_key,
    nested_get,
    nested_delete,
    nested_set,
    encode_list_index,
    decode_list_index,
    set_key,
    update_input_dict,
)
from tackle.utils.command import unpack_args_kwargs_string
from tackle.utils.help import run_help
from tackle.utils.render import wrap_jinja_braces

logger = logging.getLogger(__name__)


def merge_block_output(
        hook_output_value: Any,
        context: Context,
        append_hook_value: bool = False,
):
    """
    Block hooks have already written to the output data so to merge, need to take the
     keys from the key path and move the data up one level.
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

    # TODO: 66 - Should qualify dict here
    target_context, key_path = get_target_and_key(context=context)
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


def run_hook_exec(
        context: Context,
        hook: CompiledHookType,
        # Only jinja hooks will not have hook_call since there is never any control flow
        # associated with a jinja hook.
        hook_call: HookCallInput | None = None,
) -> Any:
    """
    Run the hook's exec method by injecting any needed params such as context and
     hook_call if they are present in the function signature.
    """
    signature = inspect.signature(hook.exec)

    injected_params = {}
    for k, v in signature.parameters.items():
        param_type = v.annotation
        if param_type is Context:
            injected_params[k] = context
        elif param_type is HookCallInput:
            injected_params[k] = hook_call
        # Types can sometimes be in quotes - ie def exec(self, context: 'Context')
        elif param_type == 'Context':
            injected_params[k] = context
        elif param_type == 'HookCallInput':
            injected_params[k] = hook_call
        else:
            raise exceptions.MalformedHookDefinitionException(
                f"The exec method in hook={hook.hook_name} has an unknown "
                f"parameter={k} with type={v} which is not supported. Only params of "
                f"type `Context` and `HookCallInput` are supported.",
                context=context, hook_name=hook,
            )

    return hook.exec(**injected_params)


def run_hook_in_dir(
        context: Context,
        hook_call: HookCallInput,
        hook: CompiledHookType,
) -> Any:
    """Run the `exec` method in a dir if `chdir` is given in `hook_call`."""
    if hook_call.chdir:
        path = os.path.abspath(os.path.expanduser(hook_call.chdir))
        if os.path.isdir(path):
            # Use contextlib to switch dirs
            with work_in(os.path.abspath(os.path.expanduser(hook_call.chdir))):
                return run_hook_exec(context=context, hook_call=hook_call, hook=hook)
        else:
            raise exceptions.HookUnknownChdirException(
                f"The specified path='{path}' to change to was not found.",
                context=context,
            ) from None
    else:
        return run_hook_exec(context=context, hook_call=hook_call, hook=hook)


def update_hook_vars(
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
):
    """
    Iterate through all the hook's fields and handle rendering along with mapping extra
     kwargs based on the `kwargs` field. Handles `render_by_default` cases where even
     if the field is not wrapped in jinja braces, it will attempt to render it. Useful
     when you have a hook whose input is always rendered. Also handles `render_exclude
     which skips rendering a field. And last it renders any fields wrapped in jinja
     braces.
    """
    # TODO: Split out to own file.
    for k, v in hook_call.model_extra.copy().items():
        # Need to check for the unquoted yaml string error here as we miss it in the
        # initial run of the macro since the key is embedded so we run it again here.
        # Handles case `key: {{value}}` which ruamel will expand into embedded dict
        # which is never the user's intention.
        v = unquoted_yaml_template_macro(value=v)

        # Handle `kwargs` field which maps unknown keys to a field
        if k not in Hook.model_fields:
            # TODO: Fix this for model_config in hook
            # if Hook.model_config['extra'] in ['allow']:
            #     continue

            # Check if the field is within the hook
            if Hook.model_fields['kwargs'].default is None:
                # The Hook has some extra field in it and we don't have a `kwargs` field
                # which will map extra args to a field so we need to raise here.
                hook_name = Hook.model_fields['hook_name'].default
                # available_fields =
                exceptions.raise_hook_parse_exception_with_link(
                    context=context,
                    Hook=Hook,
                    msg=f"The field=`{k}` is not available in the hook=`{hook_name}` "
                        f"and there is no `kwargs` mapper either. Remove that field...",
                )
                raise  # Should have raised by now
            else:
                # Map the extra fields to the `kwargs` field
                kwargs_field = Hook.model_fields['kwargs'].default
                # Check that the kwargs_field is a dict - if not it can't be mapped
                if Hook.model_fields[kwargs_field].annotation == dict:
                    # Create an empty dict if the field is not defined
                    if kwargs_field not in hook_call.model_extra:
                        hook_call.model_extra[kwargs_field] = {}
                    # Update the field with the extra field
                    hook_call.model_extra[kwargs_field].update(
                        {k: render_variable(context, v)}
                    )
                    # Remove the field from the hook_call as it is now mapped
                    hook_call.model_extra.pop(k)
                    continue
                else:
                    # Mapping additional kwargs must be to a dict field
                    raise exceptions.BadHookKwargsRefException(
                        "The hook's kwargs field references a non-dict field. Need to"
                        " fix this in the hook's definition to reference a dict field.",
                        context=context, hook_name=Hook,
                    )
        # TODO: Test / update this -> render_exclude in json_schema_extra now
        # Exclude rendering any fields defined in the `render_exclude` field
        render_exclude = Hook.model_fields['render_exclude'].default
        if render_exclude:
            if isinstance(render_exclude, list):
                # We need manually validate this here as Hook is not instantiated
                if k in render_exclude:
                    continue
            else:
                raise exceptions.MalformedHookDefinitionException(
                    "The `render_exclude` field must be a list of fields to exclude.",
                    context=context, hook_name=Hook,
                )

        # Render any field defined in the `render_exclude` field by default (ie it
        # doesn't need to be wrapped in jinja braces).
        render_by_default = Hook.model_fields['render_by_default'].default
        if render_by_default:
            if isinstance(render_by_default, list):
                # We need manually validate this here as Hook is not instantiated
                if k in render_by_default:
                    hook_call.model_extra[k] = render_variable(
                        context=context, raw=wrap_jinja_braces(v)
                    )
                    continue
            else:
                raise exceptions.MalformedHookDefinitionException(
                    "The `render_by_default` field must be a list of fields to "
                    "render even if it isn't wrapped in jinja braces (ie {{foo}}).",
                    context=context, hook_name=Hook,
                )

        # Render any field marked with `render_by_default`
        if Hook.model_fields[k].json_schema_extra is not None:
            # Need to check for this field in the `json_schema_extra`
            if 'render_by_default' in Hook.model_fields[k].json_schema_extra:
                if not isinstance(
                        Hook.model_fields[k].json_schema_extra['render_by_default'],
                        bool
                ):
                    raise exceptions.MalformedHookDefinitionException(
                        f"The `render_by_default` field in key=`{k}` must be a boolean.",
                        context=context, hook_name=Hook,
                    )
                if Hook.model_fields[k].json_schema_extra['render_by_default']:
                    if isinstance(v, str):
                        hook_call.model_extra[k] = render_variable(context,
                                                                   wrap_jinja_braces(v))
                        continue
                    # Relates to https://github.com/sudoblockio/tackle/issues/183
                    # Where we might want to have variadic arguments.
                    else:
                        logger.warning(f"Encountered a `render_by_default` field={k} "
                                       f"of type {type(v)}. Skipping rendering...")

        # Finally render any field that is left over with jinja braces
        hook_call.model_extra[k] = render_variable(context, v)


def parse_sub_context(
        context: 'Context',
        hook_target: Any,
):
    """
    Reparse a subcontext as in the case with `else` and `except` where you have to
     handle the negative side of the either `if` or `try`. Works on both looped and
     normal runs by checking the last item in the key path. Then overwrites the input
     with a new context.
    """
    if isinstance(hook_target, str):
        set_key(
            context=context,
            value=render_variable(context, hook_target),
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
            element=context.data.input,
            keys=indexed_key_path[:-3],
        )
        updated_item = [
            hook_target if i == decode_list_index(context.key_path[-1]) else None
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
            element=context.data.input,
            keys=indexed_key_path[:-2],
        )
        arrow = context.key_path[-1]
        input_dict[indexed_key_path[-2]] = {arrow: 'block', 'items': hook_target}
        walk_document(context, value=input_dict[indexed_key_path[-2]])


def new_hook(
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
):
    """Create a new instantiated hook."""
    # We clear the temporary context for hooks that have `skip_output` set and have no
    # key_path_block (ie when we have reached the base of a temporary context) as this
    # is a proxy for when we need to clear this data as it should not be carried over
    # indefinitely.
    if Hook.model_fields['skip_output'].default and len(context.key_path_block) == 0:
        context.data.temporary = {}

    try:
        hook = Hook.model_validate(hook_call.model_extra)
    except TypeError as e:
        # TODO: Improve -> This is an error when we have multiple of the same
        #  base attribute. Should not conflict in the future when we do
        #  composition on the context but for now, catching common error.
        # TODO: WIP - https://github.com/sudoblockio/tackle/issues/104
        raise exceptions.UnknownInputArgumentException(
            str(e) + " - Can't assign duplicate base fields.", context=context
        ) from None

    # This is kept loose since we might have a hook validator that raise an error which
    # is not anything specific (ie ValidationError).
    except Exception as e:
        # Handle any try / except logic
        if hook_call.try_:
            if hook_call.except_:
                # If there is an except field then we parse that as subcontext
                parse_sub_context(context=context, hook_target=hook_call.except_)
            return

        # Otherwise we need to throw
        exceptions.raise_hook_parse_exception_with_link(
            context=context,
            Hook=Hook,
            msg=str(e),
        )
        raise  # We never get here...
    return hook


def update_hook_with_kwargs_field(
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
    """
    Main parser for the hook execution which renders args, instantiates the hook, and
     calls the hook with try / except along with skip_output and merge logic.
    """
    # Render the remaining hook variables
    update_hook_vars(
        context=context,
        hook_call=hook_call,
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
            hook_output_value = run_hook_in_dir(
                context=context,
                hook_call=hook_call,
                hook=hook,
            )
        except Exception:  # noqa  - We want to catch all exceptions
            if hook_call.except_:
                parse_sub_context(
                    context=context,
                    hook_target=hook_call.except_,
                )
            return
    else:
        # Normal hook run
        hook_output_value = run_hook_in_dir(
            context=context,
            hook_call=hook_call,
            hook=hook,
        )

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
        elif context.break_:
            # We hit some hook like `return` where temporary data is not relevant
            return
        elif context.data.temporary:
            # Write the indexed output to the `data.temporary` as it was only written
            # to the `data.public` and not maintained between items in a list
            if not isinstance(context.key_path[-1], bytes):
                get_set_temporary_context(context=context)

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


class ForVariableNames(BaseModel):
    loop_targets: list | dict = None
    index_name: str = None
    value_name: str = None
    key_name: str | None = None


def get_for_loop_variable_names(
        context: 'Context',
        hook_call: HookCallInput,
) -> ForVariableNames:
    """
    Parse a hook's `for` field which can either be a reference to a list or a dict and
     inject temporary variables into the context for the iterrand and the index of the
     iteration. Abides by the following logic for injecting variables:

     `for`: list -> item + index
     `for`: dict -> key + value + index
     `for`: var in list -> var + index
     `for`: var, i in list -> var + i
     `for`: k in dict -> k + value + index
     `for`: k, v  in dict -> k + v + index
     `for`: k, v, i  in dict -> k + v + i

    Function builds a model
    """
    key_name = None
    value_name = None
    index_name = 'index'

    if isinstance(hook_call.for_, str):
        for_split = hook_call.for_.split(' in ')
        if len(for_split) == 1:  # We don't have a `foo in bar` type of expression
            # Render first variable which should be a list or dict
            loop_targets = render_variable(
                context=context,
                raw=wrap_jinja_braces(hook_call.for_),
            )
            # Assume the names as we don't have any other context
            if isinstance(loop_targets, list):
                value_name = 'item'
            elif isinstance(loop_targets, dict):
                key_name = 'key'
                value_name = 'value'
            else:
                exceptions.raise_malformed_for_loop_key(
                    context=context,
                    raw=hook_call.for_,
                    loop_targets=loop_targets,
                )

        elif len(for_split) == 2:  # We have the syntax of `for: foo in bar`
            # Render second variable which should be a list or dict
            loop_targets = render_variable(
                context=context,
                raw=wrap_jinja_braces(for_split[1]),
            )
            names_split = [i.strip() for i in for_split[0].split(',')]
            if isinstance(loop_targets, list):
                if len(names_split) == 1:
                    value_name = names_split[0]
                elif len(names_split) == 2:
                    index_name = names_split[0]
                    value_name = names_split[1]
                else:
                    # TODO: Link to flow control section of docs for loops
                    docs_link = f"{exceptions.DOCS_DOMAIN}/"
                    raise exceptions.MalformedTemplateVariableException(
                        "The supplied args are not valid. Must be in form "
                        f"value, [index]. See docs {docs_link}/",
                        context=context)
            elif isinstance(loop_targets, dict):
                if len(names_split) == 1:
                    key_name = names_split[0]
                    value_name = 'value'
                elif len(names_split) == 2:
                    key_name = names_split[0]
                    value_name = names_split[1]
                elif len(names_split) == 3:
                    key_name = names_split[0]
                    value_name = names_split[1]
                    index_name = names_split[2]
                else:
                    # TODO: Link to flow control section of docs for loops
                    docs_link = f"{exceptions.DOCS_DOMAIN}/"
                    raise exceptions.MalformedTemplateVariableException(
                        "The supplied args are not valid. Must be in form "
                        f"key, [value], [index]. See docs {docs_link}", context=context)
            else:
                exceptions.raise_malformed_for_loop_key(
                    context=context,
                    raw=hook_call.for_,
                    loop_targets=loop_targets,
                )
        else:
            raise exceptions.MalformedTemplateVariableException(
                f"For some reason you put `in` twice in the `for` key - "
                f"{hook_call.for_}. Don't do that...", context=context)

    elif isinstance(hook_call.for_, list):
        # We have a list literal supplied and assume variable names
        loop_targets = hook_call.for_
        value_name = 'item'
        index_name = 'index'

    elif isinstance(hook_call.for_, dict):
        # We have a dict literal supplied and assume variable names
        loop_targets = hook_call.for_
        key_name = 'key'
        value_name = 'value'
        index_name = 'index'

    else:
        # This is probably impossible to hit since we already validate this model.
        actual_type = type(hook_call.for_).__name__
        raise exceptions.MalformedTemplateVariableException(
            f"The `for` field must be a list/object or string reference to "
            f"a list/object. The value is of type `{actual_type}`.", context=context,
        ) from None

    try:
        return ForVariableNames(
            loop_targets=loop_targets,
            key_name=key_name,
            value_name=value_name,
            index_name=index_name,
        )
    except ValidationError as e:
        raise exceptions.MalformedTemplateVariableException(
            f"The `for` field after parsing is invalid - \n{e.__str__}.",
            context=context,
        ) from None


def evaluate_for(
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
):
    """Run the parse_hook function in a loop with temporary variables."""
    vars = get_for_loop_variable_names(context=context, hook_call=hook_call)
    hook_call.for_ = None

    if len(vars.loop_targets) == 0:
        return

    if isinstance(vars.loop_targets, list):
        # if hook_call.merge:
        #     set_key(context=context, value=[])
        # TODO: Wtf is going on here?
        if not hook_call.merge:
            set_key(context=context, value=[])
        for i, l in (
                enumerate(vars.loop_targets)
                if not render_variable(context, hook_call.reverse)
                else reversed(list(enumerate(vars.loop_targets)))
        ):
            # Create temporary variables in the context to be used in the loop.
            context.data.existing.update({
                vars.index_name: i,
                vars.value_name: l,
            })
            # Append the index to the keypath
            context.key_path.append(encode_list_index(i))
            # Reparse the hook with the new temp vars in place
            parse_hook(
                context=context,
                hook_call=hook_call.__copy__(),
                Hook=Hook,
                append_hook_value=True,
            )
            context.key_path.pop()

    elif isinstance(vars.loop_targets, dict):
        if hook_call.merge:
            # To merge into a list
            set_key(context=context, value=[])
        elif not hook_call.merge:
            set_key(context=context, value=[])
        for i, (k, v) in (
                enumerate(vars.loop_targets.items())
                if not render_variable(context, hook_call.reverse)
                else reversed(list(enumerate(vars.loop_targets)))
        ):
            # Create temporary variables in the context to be used in the loop.
            context.data.existing.update({
                vars.index_name: i,
                vars.value_name: v,
                vars.key_name: k,
            })
            # Append the index to the keypath
            context.key_path.append(encode_list_index(i))
            # Reparse the hook with the new temp vars in place
            parse_hook(
                context=context,
                hook_call=hook_call.__copy__(),
                Hook=Hook,
                append_hook_value=True,
            )
            context.key_path.pop()
    else:
        raise Exception("Should never happen...")

    # Remove temp variables
    try:
        context.data.existing.pop(vars.key_name)
        context.data.existing.pop(vars.value_name)
        context.data.existing.pop(vars.index_name)
    except KeyError:
        pass


def parse_hook_loop(
        *,
        context: 'Context',
        hook_call: HookCallInput,
        Hook: CompiledHookType,
        append_hook_value: bool = None,
):
    """Parse hook call for loops. Ex. `key->: a_hook --for a_list`"""
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
    """
    Evaluate the if/when condition and return bool. `if` conditions are evaluated within
     a loop whereas `when` conditions are evaluated before a loop.

    Ex "if": `key->: a_hook --if i!=1 --for i in [1,2]`
     - Only i=2 will be looped
    Ex "when": `key->: a_hook --when foo=='bar' --for [1,2]`
     - Will only run if foo=='bar' evaluates as true
    """

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
        # `if` does not exist so True
        return True
    else:
        # Render the `if` condition
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
            hook_target=hook_call.else_,
        )


def evaluate_args(
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
            # We are at the last argument mapping, so we need to join the remaining
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
                    # hook_name = Hook.identifier.split('.')[-1]
                    # if hook_name == '':
                    #     hook_name = 'default'
                    # raise exceptions.UnknownArgumentException(
                    #     f"The {hook_name} hook does not take any "
                    #     f"arguments. Hook argument {v} caused an error.",
                    #     context=context,
                    # ) from None
                    raise exceptions.UnknownArgumentException(
                        "",
                        context=context,
                    ) from None


                else:
                    raise exceptions.UnknownArgumentException(
                        f"The hook {hook_dict['hook_name']} takes the following indexed"
                        f"arguments -> {hook_args} which does not map to the arg {v}.",
                        context=context,
                    ) from None


def run_hook_at_key_path(
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
    args = var_hook_macro(args)

    # Look up the hook from the imported providers
    first_arg = args.pop(0)
    Hook = get_hook(
        context=context,
        hook_name=first_arg,
        args=args,
        kwargs=kwargs,
        throw=True
    )

    # `args` can be a kwarg (ie `tackle --args foo`) and is manually added to args var
    if 'args' in kwargs:
        # For calling hooks, you can manually provide the hook with args. Useful for
        # calling declarative hooks that want to have their args inserted from rendering
        # or as a kwarg (ie tackle: {args: foo})
        hook_args = kwargs.pop('args')
        if isinstance(hook_args, list):
            args += hook_args
        else:
            args += [hook_args]

    # Associate hook arguments provided in the call with hook attributes
    evaluate_args(
        context=context,
        args=args,
        hook_dict=hook_dict,
        Hook=Hook,
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
    Traverse a document looking for hook calls and running those hooks. Here we are
     keeping track of which keys are traversed in a list called `key_path` with strings
     as dict keys and byte encoded integers for list indexes.
    """
    if isinstance(value, dict):
        # Handle expanded expressions - ie key:\n  ->: hook_name args
        if '->' in value.keys():
            # Public hook calls
            context.key_path.append('->')
            # We need to copy this value because it could be reused in a loop
            v = value.copy()
            hook_str = v.pop('->')
            run_hook_at_key_path(
                context=context,
                hook_dict=v,
                hook_str=hook_str,
            )
            context.key_path.pop()
            return
        elif '_>' in value.keys():
            # Private hook calls
            context.key_path.append('_>')
            v = value.copy()
            hook_str = v.pop('_>')
            run_hook_at_key_path(
                context=context,
                hook_dict=v,
                hook_str=hook_str,
            )
            context.key_path.pop()
            return
        elif value == {}:
            set_key(context=context, value={})
            return

        # Iterate through all the keys now of a dict since we know it is not a hook
        for k, v in value.copy().items():
            context.key_path.append(k)
            v = key_macro(context=context, value=v)
            walk_document(context=context, value=v)  # recurse
            context.key_path.pop()
            if context.break_:
                return

    # Non-hook calls recurse through inputs
    elif isinstance(value, list):
        # Handle empty lists
        if len(value) == 0:
            set_key(context=context, value=value)
        else:
            if context.key_path:
                # When we are in a list we can pre-empt setting it in-case of false
                # conditionals and would rather have an empty list than missing key
                set_key(context, [])
            for i, v in enumerate(value.copy()):
                context.key_path.append(encode_list_index(i))
                walk_document(context, v)
                context.key_path.pop()
    else:
        # Nothing left to do but run the hook
        # try:
        set_key(context=context, value=value)
        # except (TypeError, AttributeError) as e:
        #     print(e)
        #     raise e


def run_declarative_hook(
        context: 'Context',
        hook_name: str,
) -> Any:
    """
    Function to run hooks called from the command line which requires different logic
     than when hooks are called when parsing. For example:

     `tackle file.yaml a_hook an_arg_or_hook --a_kwarg a_kwarg_value --a_flag`

     Here we will need to line up these args / kwargs / flags supplied via command line
     to items within the source. Args could be references to hooks or args to a hook.

    Note: this is a lot of the same logic as seen in other places a hook is called but
     specific to declarative hooks which are called from the command line. Other
     versions of this logic exist in parser.run_hook and render.JinjaHook but are all
     slightly different based on the use case.
    """
    if hook_name == DEFAULT_HOOK_NAME:
        Hook = context.hooks.default
    else:
        # Have already qualified that this hook exists
        Hook = context.hooks.public[hook_name]

    if isinstance(Hook, LazyBaseHook):
        # Unless it is a python hook, this will need to be run to get CompiledHookType
        Hook = create_dcl_hook(
            context=context,
            hook_name=hook_name,
            hook_input_raw=Hook.input_raw.copy(),
        )

    # Handle kwargs
    kwargs = {}
    for k, v in context.input.kwargs.copy().items():
        # Consume input kwargs and set them as defaults + validate with hook's field type
        if k in Hook.model_fields:
            kwargs.update({k: context.input.kwargs.pop(k)})

    # Handle args
    arg_dict = {}
    num_popped = 0
    for i, arg in enumerate(context.input.args.copy()):
        # For running hooks in tackle files (ie not in `hooks` dir), we run this logic
        # as the hook is already compiled.
        if arg in Hook.model_fields and Hook.model_fields[arg].annotation == Callable:
            # Consume the args
            context.input.args.pop(i - num_popped)
            num_popped += 1

            # Gather the function's dict so it can be compiled into a runnable hook
            hook_dict = Hook.model_fields[arg].default.input_raw.copy()

            # Add inheritance from base function fields
            for field_name in Hook.model_fields['hook_field_set'].default:
                # Base method should not override child.
                if field_name not in hook_dict:
                    # TODO: Figure out if doing the default here is right - it could be
                    #  set by now.
                    hook_dict[field_name] = Hook.model_fields[field_name].default

            # Compile hook method
            Hook = create_dcl_hook(
                context=context,
                hook_name=arg,
                hook_input_raw=hook_dict,
            )
        elif arg == 'help' and i == len(context.input.args) - 1:
            # Prioritize help if it is the last arg
            run_help(context=context, Hook=Hook)  # Exit 0

        elif Hook.model_fields['args'].default:
            # Handle the `args` field which maps to args
            if 'args' in Hook.model_fields:
                evaluate_args(
                    context=context,
                    args=context.input.args,
                    hook_dict=arg_dict,
                    Hook=Hook,
                )
        else:
            # Throw error as we have nothing to map the arg to
            hook_name = Hook.model_fields['hook_name'].default
            if hook_name == DEFAULT_HOOK_NAME:
                msg = "default hook"
            else:
                msg = f"hook='{hook_name}'"
            raise exceptions.UnknownInputArgumentException(
                f"The {msg} was supplied the arg='{arg}' and does not take any "
                "arguments. Exiting.",
                context=context,
            ) from None

    try:
        hook = Hook(**kwargs, **arg_dict)
    except ValidationError as e:

        raise exceptions.MalformedHookFieldException(
            str(e),
            hook_name=hook_name,
            context=context,
        ) from None
    return run_hook_exec(context=context, hook_call=None, hook=hook)


def raise_if_args_exist(
        context: 'Context',
        Hook: CompiledHookType,
):
    """
    Raise an error if not all the args / kwargs / flags have been consumed which would
     mean the user supplied extra vars and should be yelled at.
    """
    msgs = []
    if len(context.input.args) != 0:
        msgs.append(f"args {', '.join(context.input.args)}")
    if len(context.input.kwargs) != 0:
        missing_kwargs = ', '.join(
            [f"{k}={v}" for k, v in context.input.kwargs.items()])
        msgs.append(f"kwargs {missing_kwargs}")
    if len(msgs) != 0:
        if Hook:
            hook_name = Hook.model_fields['hook_name']
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


DEFAULT_HOOK_NAME = '_default'


def parse_input_args_for_hooks(context: 'Context'):
    """
    Process input args/kwargs/flags based on if the args relate to the default hook or
     some public hook (usually declarative). Once the hook has been identified, the
     args/kwargs/flags are consumed and if there are any args left, an error is raised.
    """
    num_args = len(context.input.args)
    if num_args == 0:
        if context.hooks.default:  # Default hook (no args)
            context.data.public = run_declarative_hook(
                context=context,
                hook_name=DEFAULT_HOOK_NAME,
            )
    elif num_args == 1 and \
            context.input.args[0] == 'help' and \
            context.hooks.default is not None:
        run_help(context=context, Hook=context.hooks.default)
    elif num_args == 1 and context.input.args[0] == 'help':
        run_help(context=context)
    elif num_args != 0:  # With args
        # Prioritize public_hooks (ie non-default hook) because if the hook exists,
        # then we should consume the arg there instead of using the arg as an arg for
        # default hook because otherwise the public hook would be unreachable.
        if context.input.args[0] in context.hooks.public:
            # Search within the public hook for additional args that could be
            # interpreted as methods which always get priority over consuming the arg
            # as an arg within the hook itself.
            hook_name = context.input.args.pop(0)  # Consume arg
            context.data.public = run_declarative_hook(
                context=context,
                hook_name=hook_name,
            )
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                Hook=context.hooks.public[hook_name],
            )
        elif context.hooks.default:
            context.data.public = run_declarative_hook(
                context=context,
                hook_name=DEFAULT_HOOK_NAME,
            )
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                Hook=context.hooks.default,
            )
        else:
            raise_if_args_exist(  # Raise if there are any args left
                context=context,
                Hook=context.hooks.default,  # This is None if it does not exist
            )
    else:
        # If there are no declarative hooks defined, use the kwargs to override values
        #  within the context.
        context.data.input = update_input_dict(
            input_dict=context.data.input,
            update_dict=context.input.kwargs,
        )
    # # TODO: This should be moved - It is not part of this logic
    # # Apply overrides
    # context.data.input = update_input_dict(
    #     input_dict=context.data.input,
    #     update_dict=context.data.overrides,
    # )


def split_input_data(context: 'Context'):
    """
    Split the raw_input from a tackle file into pre/post_input objects along with
     pulling out any declarative hooks and putting them into the public / private keys
     of the hooks class.

     pre_input - data before the first hook definition
     post_input - data after the first hook definition

     This allows us to import hooks on the top of a document so that they are available
     for use before the hooks are compiles and the args/kwargs are used to call them.
     See TODO [docs]
    """
    if isinstance(context.data.raw_input, list):
        # Nothing to do. Our input is a list and no hooks or pre/post data can be built
        # TODO: When parsing yaml - check if we have a split document (ie with `---`)
        #  which will be read as a list in which case we need to split that up somehow
        return

    pre_data_flag = True
    for k, v in context.data.raw_input.items():
        hook_flag = re.match(r'^[a-zA-Z0-9\_]*(<\-|<\_)$', k)  # noqa
        if pre_data_flag and not hook_flag:
            context.data.pre_input.update({k: v})
        elif hook_flag:
            pre_data_flag = False
            hook_name = k[:-2]
            arrow = k[-2:]
            try:
                dcl_hook = LazyBaseHook(
                    input_raw=v,
                    is_public=True if arrow == '<-' else False,
                )
            except ValidationError:
                raise exceptions.MalformedHookDefinitionException(
                    f"Declarative hooks definitions need to be a map, not a "
                    f"'{type(v)}'.", context=context, hook_name=hook_name,
                )
            if hook_name == "":
                # dcl_hook is the default hook
                context.hooks.default = dcl_hook
            elif arrow == '<-':  # public hook
                context.hooks.public[hook_name] = dcl_hook
            elif arrow == '<_':  # private hook
                context.hooks.private[hook_name] = dcl_hook
            else:
                raise Exception("This should never happen")
        else:
            context.data.post_input.update({k: v})


def parse_context(context: 'Context', call_hooks: bool = True):
    """
    Main entrypoint to parsing a context. When importing tackle providers, we don't want
     to call_hooks so it is set to false. Otherwise, we might call hooks (ie true).
    """
    # Split the input data so that the pre/post inputs are separated from the hooks
    split_input_data(context=context)
    # Parse the pre_input before qualifying the help for imports and other
    if context.data.pre_input:
        context.data.input = context.data.pre_input
        walk_document(context=context, value=context.data.pre_input)
    # Get the remaining declarative hooks out of the context
    if call_hooks:  # Run except on import
        # We give hooks on import and don't want to evaluate args then
        parse_input_args_for_hooks(context=context)  # Evaluate args for calling hooks
    # Parse the post_input after running hooks if any
    if context.data.post_input:
        context.data.input = context.data.post_input
        walk_document(context=context, value=context.data.post_input)
