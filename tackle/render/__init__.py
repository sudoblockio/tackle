"""Main entrypoint for rendering."""
import ast
from jinja2 import meta
from inspect import signature

from tackle.render.special_vars import special_variables
from tackle.render.environment import StrictEnvironment
from tackle.exceptions import UnknownTemplateVariableException
from typing import TYPE_CHECKING, Any

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
        render_string(context, raw)
    elif isinstance(raw, dict):
        return {
            render_string(context, k): render_variable(context, v)
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return [render_variable(context, v) for v in raw]
    else:
        return raw

    return render_string(context, raw)


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

    env = StrictEnvironment(context=context.input_dict)
    template = env.from_string(raw)
    # Extract variables
    variables = meta.find_undeclared_variables(env.parse(raw))

    if len(variables) == 0:
        for i in env.globals.keys():
            if i in raw:
                # TODO: Perhaps change this into a search to see if `for i in globals in raw`
                raise Exception(
                    f"No renderable variables found in {raw}. Could be "
                    f"because there is a collision with a global variable "
                    f"{','.join(list(env.globals.keys()))}. See "
                    f"https://github.com/pallets/jinja/issues/1580"
                )

    # Build a render context by inspecting the renderable variables
    render_context = {}
    unknown_variable = []
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
            unknown_variable.append(v)

    try:
        rendered_template = template.render(render_context)
    except Exception as e:
        if len(unknown_variable) != 0:
            raise UnknownTemplateVariableException(
                f"Variable {unknown_variable} unknown."
            )
        raise e

    try:
        # This will error on strings
        return ast.literal_eval(rendered_template)
    except (ValueError, SyntaxError):
        return rendered_template
