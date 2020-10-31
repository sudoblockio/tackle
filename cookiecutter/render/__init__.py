"""Main entrypoint for rendering."""
import ast
import re
import six

from cookiecutter.render.special_vars import get_vars
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cookiecutter.models import Context


def build_render_context(c: 'Context'):
    """Depending on the generation build a context.

    For cookiecutter, enforce standards ie '{{ cookiecutter.var }}' but for tackle,
    support both ie '{{ cookiecutter.var }}' and '{{ var }}'.
    """
    # TODO: get_vars should be instantiated earlier...
    special_variables = get_vars(c)
    if c.tackle_gen == 'cookiecutter':
        render_context = {c.context_key: c.output_dict}
        render_context.update(special_variables)
    else:
        render_context = dict(c.output_dict, **{c.context_key: dict(c.output_dict)})
        render_context.update(special_variables)
    return render_context


def render_variable(c: 'Context', raw: Any):
    """Render the next variable to be displayed in the user prompt.

    Inside the prompting taken from the cookiecutter.json file, this renders
    the next variable. For example, if a project_name is "Peanut Butter
    Cookie", the repo_name could be be rendered with:

        `{{ cookiecutter.project_name.replace(" ", "_") }}`.

    This is then presented to the user as the default.

    :param Environment env: A Jinja2 Environment object.
    :param raw: The next value to be prompted for by the user.
    :param dict cc_dict: The current context as it's gradually
        being populated with variables.
    :return: The rendered value for the default variable.
    """
    if raw is None:
        return None
    elif isinstance(raw, dict):
        return {render_variable(c, k): render_variable(c, v) for k, v in raw.items()}
    elif isinstance(raw, list):
        return [render_variable(c, v) for v in raw]
    elif not isinstance(raw, six.string_types):
        raw = str(raw)

    template = c.env.from_string(raw)

    render_context = build_render_context(c)
    # This is where we build both the {{ cookiecutter.var }} and {{ var }} contexts
    rendered_template = template.render(render_context)

    # Tackle evaluates dicts, lists, and bools as literals where as cookiecutter
    # renders them to string
    if c.tackle_gen == 'cookiecutter':
        return rendered_template

    if raw == '{{ nuki }}':
        print()

    REGEX = [
        r'^\[.*\]$',  # List
        r'^\{.*\}$',  # Dict
        r'^True$|^False$',  # Boolean
        r'^\d+$',  # Integer
        r'^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$',  # Float
    ]
    for r in REGEX:
        if bool(re.search(r, rendered_template)):
            """If variable looks like list, return literal list"""
            return ast.literal_eval(rendered_template)

    return rendered_template
