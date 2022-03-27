import re
import ast
from jinja2 import meta
from jinja2.exceptions import UndefinedError
from inspect import signature
from typing import TYPE_CHECKING, Any
from pydantic import ValidationError

from tackle.special_vars import special_variables
from tackle.exceptions import UnknownTemplateVariableException

if TYPE_CHECKING:
    from tackle.models import Context


def wrap_braces_if_not_exist(value):
    """Wrap with braces if they don't exist."""
    if '{{' in value and '}}' in value:
        # Already templated
        return value
    return '{{' + value + '}}'


def wrap_jinja_braces(value):
    """Wrap a string with braces so it can be templated."""
    if isinstance(value, str):
        return wrap_braces_if_not_exist(value)
    # Nothing else can be wrapped
    return value


def render_variable(context: 'Context', raw: Any):
    """
    Render the raw input. Does recursion with dict and list inputs, otherwise renders
    string.

    :param raw: The value to be rendered.
    :return: The rendered value as literal type.
    """
    if raw is None:
        return None
    elif isinstance(raw, str):
        return render_string(context, raw)
    elif isinstance(raw, dict):
        return {
            render_string(context, k): render_variable(context, v)
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return [render_variable(context, v) for v in raw]
    else:
        return raw


def render_string(context: 'Context', raw: str):
    """
    Render strings by first extracting renderable variables then build a render context
    from the output_dict, then existing context, and last looks up special variables.
    After the value has been rendered it is returned as literal so as to preserve the
    original type of the value.

    :return: The literal value if the output is a string / list / dict / float / int
    """
    if '{{' not in raw:
        return raw

    template = context.env_.from_string(raw)
    # Extract variables
    variables = meta.find_undeclared_variables(context.env_.parse(raw))

    # Build a render context by inspecting the renderable variables
    render_context = {}
    unknown_variables = []
    for v in variables:
        # Variables in the current output_dict take precedence
        if v in context.output_dict:
            render_context.update({v: context.output_dict[v]})
        elif v in context.existing_context:
            render_context.update({v: context.existing_context[v]})
        elif v in special_variables:
            # If it is a special variable we need to check if the call requires
            # arguments, only context supported now.
            argments = list(signature(special_variables[v]).parameters)
            if len(argments) == 0:
                render_context.update({v: special_variables[v]()})
            elif 'context' in argments:
                render_context.update({v: special_variables[v](context)})
            else:
                raise ValueError("This should never happen.")
        else:
            unknown_variables.append(v)

    # Evaluate any hooks and insert into jinja environment globals
    if len(unknown_variables) != 0:
        # Unknown variables can be real unknown variables, preloaded jinja globals or
        # hooks which need to be inserted into the global env so that they can be called
        for i in unknown_variables:
            if i in context.provider_hooks:
                context.env_.globals[i] = context.provider_hooks[i](
                    input_dict=context.input_dict,
                    output_dict=context.output_dict,
                    existing_context=context.existing_context,
                    no_input=context.no_input,
                    calling_directory=context.calling_directory,
                    calling_file=context.calling_file,
                    provider_hooks=context.provider_hooks,
                    key_path=context.key_path,
                    verbose=context.verbose,
                ).wrapped_exec

    try:
        rendered_template = template.render(render_context)
        if rendered_template.startswith('<bound method BaseHook'):
            # Handle unknown variables that are the same as hook_types issues/55
            raise UndefinedError

        # Check for ambiguous globals like `namespace` tackle-box/issues/19
        match = re.search(r'\<class \'(.+?)\'>', rendered_template)
        if match:
            ambiguous_key = match.group(1).split('.')[-1].lower()
            if ambiguous_key in context.output_dict:
                rendered_template = context.output_dict[ambiguous_key]
            elif match.group(1) in context.existing_context:
                rendered_template = context.existing_context[ambiguous_key]

    except ValidationError as e:
        # For pydantic validation errors
        raise e

    except UndefinedError as e:
        if len(unknown_variables) != 0:
            raise UnknownTemplateVariableException(
                f"Variable{'s' if len(unknown_variables) != 1 else ''} {' '.join(unknown_variables)} unknown."
            )
        raise e

    try:
        # This will error on strings
        return ast.literal_eval(rendered_template)
    except (ValueError, SyntaxError):
        return rendered_template
