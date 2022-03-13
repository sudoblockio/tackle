import re
import ast
from jinja2 import Environment, StrictUndefined, meta
from inspect import signature
from pydantic.main import ModelMetaclass
from typing import TYPE_CHECKING, Any

from tackle.render.special_vars import special_variables
from tackle.render.environment import StrictEnvironment
from tackle.exceptions import UnknownTemplateVariableException
from tackle.exceptions import UnknownExtension

if TYPE_CHECKING:
    from tackle.models import Context


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
        context: Context = kwargs.pop('context', {})

        provider_extensions = [
            v.identifier
            for _, v in context.provider_hooks.items()
            if isinstance(v, ModelMetaclass)
        ]

        default_extensions = [
            'tackle.providers.paths.hooks.dirs.MakeTempDirectoryHook',
            'tackle.render.extensions.JsonifyExtension',
            'tackle.render.extensions.RandomStringExtension',
        ]
        # 'tackle.providers.console.printer.PrintHook',
        # PrintHook,
        # 'jinja2_time.TimeExtension',
        # 'tackle.providers.console.markdown.MarkdownPrintHook',
        # 'tackle.providers.console.printer.PrintHook',

        extensions = provider_extensions  # + self._read_extensions(context)

        try:
            # , output_dict=context.output_dict
            super(ExtensionLoaderMixin, self).__init__(extensions=extensions, **kwargs)
        except ImportError as err:
            raise UnknownExtension('Unable to load extension: {}'.format(err))

    # TODO: Disable this until a pattern is settled on in tackle - legacy
    def _read_extensions(self, context):
        """Return list of extensions as str to be passed on to the Jinja2 env.

        If context does not contain the relevant info, return an empty
        list instead.
        """
        try:
            extensions = context['_extensions']
        except (KeyError, TypeError):
            return []
        else:
            return [str(ext) for ext in extensions]


class StrictEnvironment(ExtensionLoaderMixin, Environment):
    """Create strict Jinja2 environment.

    Jinja2 environment will raise error on undefined variable in template-
    rendering context.
    """

    def __init__(self, **kwargs):
        """Set the standard Tackle StrictEnvironment.

        Also loading extensions defined in cookiecutter.json's _extensions key.
        """
        super(StrictEnvironment, self).__init__(undefined=StrictUndefined, **kwargs)


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

    if context.env is None:
        context.env = StrictEnvironment(context=context)

    template = context.env.from_string(raw)
    # Extract variables
    variables = meta.find_undeclared_variables(context.env.parse(raw))

    # if len(variables) == 0:
    #     for i in env.globals.keys():
    #         if i in raw:
    #             # TODO: Perhaps change this into a search to see if `for i in globals in raw`
    #             # TODO: Convert to compiling regex for searching for globals
    #             raise Exception(
    #                 f"No renderable variables found in {raw}. Could be "
    #                 f"because there is a collision with a global variable "
    #                 f"{','.join(list(env.globals.keys()))}. See "
    #                 f"https://github.com/pallets/jinja/issues/1580"
    #             )

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
        # Check for ambigous globals like `namespace` tackle-box/issues/19
        match = re.search(r'\<class \'(.+?)\'>', rendered_template)
        if match:
            ambiguous_key = match.group(1).split('.')[-1].lower()
            if ambiguous_key in context.output_dict:
                rendered_template = context.output_dict[ambiguous_key]
            elif match.group(1) in context.existing_context:
                rendered_template = context.existing_context[ambiguous_key]

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
