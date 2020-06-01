# -*- coding: utf-8 -*-

"""Jinja2 environment and extensions loading."""
import ast
import re

import six
from jinja2 import Environment, StrictUndefined

from cookiecutter.exceptions import UnknownExtension


class ExtensionLoaderMixin(object):
    """Mixin providing sane loading of extensions specified in a given context.

    The context is being extracted from the keyword arguments before calling
    the next parent class in line of the child.
    """

    def __init__(self, **kwargs):
        """Initialize the Jinja2 Environment object while loading extensions.

        Does the following:

        1. Establishes default_extensions (currently just a Time feature)
        2. Reads extensions set in the cookiecutter.json _extensions key.
        3. Attempts to load the extensions. Provides useful error if fails.
        """
        context = kwargs.pop('context', {})

        default_extensions = [
            'cookiecutter.extensions.JsonifyExtension',
            'cookiecutter.extensions.RandomStringExtension',
            'cookiecutter.extensions.SlugifyExtension',
            'jinja2_time.TimeExtension',
        ]
        extensions = default_extensions + self._read_extensions(context)

        try:
            super(ExtensionLoaderMixin, self).__init__(extensions=extensions, **kwargs)
        except ImportError as err:
            raise UnknownExtension('Unable to load extension: {}'.format(err))

    def _read_extensions(self, context):
        """Return list of extensions as str to be passed on to the Jinja2 env.

        If context does not contain the relevant info, return an empty
        list instead.
        """
        try:
            extensions = context['cookiecutter']['_extensions']
        except KeyError:
            return []
        else:
            return [str(ext) for ext in extensions]


class StrictEnvironment(ExtensionLoaderMixin, Environment):
    """Create strict Jinja2 environment.

    Jinja2 environment will raise error on undefined variable in template-
    rendering context.
    """

    def __init__(self, **kwargs):
        """Set the standard Cookiecutter StrictEnvironment.

        Also loading extensions defined in cookiecutter.json's _extensions key.
        """
        super(StrictEnvironment, self).__init__(undefined=StrictUndefined, **kwargs)


def render_variable(env, raw, cookiecutter_dict):
    """Render the next variable to be displayed in the user prompt.

    Inside the prompting taken from the cookiecutter.json file, this renders
    the next variable. For example, if a project_name is "Peanut Butter
    Cookie", the repo_name could be be rendered with:

        `{{ cookiecutter.project_name.replace(" ", "_") }}`.

    This is then presented to the user as the default.

    :param Environment env: A Jinja2 Environment object.
    :param raw: The next value to be prompted for by the user.
    :param dict cookiecutter_dict: The current context as it's gradually
        being populated with variables.
    :return: The rendered value for the default variable.
    """
    if raw is None:
        return None
    elif isinstance(raw, dict):
        return {
            render_variable(env, k, cookiecutter_dict): render_variable(
                env, v, cookiecutter_dict
            )
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return [render_variable(env, v, cookiecutter_dict) for v in raw]
    elif not isinstance(raw, six.string_types):
        raw = str(raw)

    template = env.from_string(raw)

    rendered_template = template.render(cookiecutter=cookiecutter_dict)

    LIST_REGEX = r'^\[.*\]$'
    if bool(re.search(LIST_REGEX, rendered_template)):
        """If variable looks like list, return literal list"""
        return ast.literal_eval(rendered_template)

    return rendered_template
