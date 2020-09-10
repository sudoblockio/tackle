"""Main entrypoint for rendering."""
import ast
import re

import six

import cookiecutter as cc
from cookiecutter.render.special_vars import get_vars


def render_variable(env, raw, cc_dict, context_key):
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
        return {
            render_variable(env, k, cc_dict, context_key): render_variable(
                env, v, cc_dict, context_key
            )
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return [render_variable(env, v, cc_dict, context_key) for v in raw]
    elif not isinstance(raw, six.string_types):
        raw = str(raw)

    template = env.from_string(raw)

    special_variables = get_vars(context_key, cc_dict)
    render_context = {context_key: cc_dict}
    render_context.update(special_variables)
    rendered_template = template.render(render_context)

    if cc.repository.cookiecutter_gen == 'nukikata':  # noqa
        # Nukikata evaluates dicts, lists, and bools as literals where as cookiecutter
        # renders them to string

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
