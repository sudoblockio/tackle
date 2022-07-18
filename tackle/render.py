import re
import ast
from jinja2 import meta
from jinja2.exceptions import UndefinedError
from inspect import signature
from typing import TYPE_CHECKING, Any
from pydantic import ValidationError

from tackle.special_vars import special_variables
from tackle.exceptions import (
    UnknownTemplateVariableException,
    MissingTemplateArgsException,
)

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
    from the public_context, then existing context, and last looks up special variables.
    After the value has been rendered it is returned as literal so as to preserve the
    original type of the value.

    :return: The literal value if the output is a string / list / dict / float / int
    """
    if '{{' not in raw:
        return raw

    template = context.env_.from_string(raw)
    # Extract variables
    variables = meta.find_undeclared_variables(context.env_.parse(raw))

    # We need to make a list of used hooks so that we can remove them from the jinja
    # environment later.
    used_hooks = []

    # Build a render context by inspecting the renderable variables
    render_context = {}
    unknown_variables = []
    for v in variables:
        # Variables in the current public_context take precedence
        if context.temporary_context and v in context.temporary_context:
            render_context.update({v: context.temporary_context[v]})
        elif context.public_context and v in context.public_context:
            render_context.update({v: context.public_context[v]})
        elif context.private_context and v in context.private_context:
            render_context.update({v: context.private_context[v]})
        elif context.existing_context and v in context.existing_context:
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
                from tackle.models import LazyBaseFunction

                used_hooks.append(i)

                jinja_hook = context.provider_hooks[i]
                if isinstance(jinja_hook, LazyBaseFunction):
                    # Case where hook is declarative (ie a with internal nomenclature,
                    #  a function)...
                    from tackle.parser import create_function_model

                    jinja_hook.dict().update(
                        {
                            'input_context': context.input_context,
                            'public_context': context.public_context,
                            'existing_context': context.existing_context,
                            'no_input': context.no_input,
                            'calling_directory': context.calling_directory,
                            'calling_file': context.calling_file,
                            'provider_hooks': context.provider_hooks,
                            'key_path': context.key_path,
                            'verbose': context.verbose,
                        }
                    )

                    # Need to instantiate the hook before passing the wrapped_exec
                    context.env_.globals[i] = create_function_model(
                        context, i, jinja_hook.dict()
                    )().wrapped_exec
                else:
                    context.env_.globals[i] = jinja_hook(
                        input_context=context.input_context,
                        public_context=context.public_context,
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

        # Need to remove the hook from the globals as if it is called a second time,
        # it is no longer an unknown variable and will use the prior arguments if they
        # have not been re-instantiated.
        for i in used_hooks:
            context.env_.globals.pop(i)

        # # TODO: RM?
        if rendered_template.startswith('<bound method BaseHook'):
            # Handle unknown variables that are the same as hook_types issues/55
            raise UndefinedError(
                f"A variable `{'/'.join(used_hooks)}` is the same as "
                f"a hook and either not declared as a variable or "
                f"doesn't have arguments. Consider changing."
            )

        # Check for ambiguous globals like `namespace` tackle-box/issues/19
        match = re.search(r'\<class \'(.+?)\'>', rendered_template)
        if match:
            ambiguous_key = match.group(1).split('.')[-1].lower()
            if ambiguous_key in context.public_context:
                rendered_template = context.public_context[ambiguous_key]
            elif match.group(1) in context.existing_context:
                rendered_template = context.existing_context[ambiguous_key]

    except (TypeError, UndefinedError) as e:
        # Raised when the wrong type is provided to a hook
        raise UnknownTemplateVariableException(str(e), context=context) from None

    except ValidationError as e:
        # Raised when the wrong type is provided to a hook
        raise MissingTemplateArgsException(str(e), context=context) from None

    try:
        # This will error on strings
        return ast.literal_eval(rendered_template)
    except (ValueError, SyntaxError):
        return rendered_template
