import re
from jinja2 import meta
from jinja2.exceptions import UndefinedError, TemplateSyntaxError
from inspect import signature
from typing import TYPE_CHECKING, Any, Callable
from pydantic import ValidationError
from pydantic.main import ModelMetaclass

from tackle.hooks import LazyBaseFunction
from tackle.special_vars import special_variables
from tackle.exceptions import (
    UnknownTemplateVariableException,
    MissingTemplateArgsException,
    MalformedTemplateVariableException,
)
from tackle.utils.imports import get_public_or_private_hook
from tackle.utils.command import literal_eval

if TYPE_CHECKING:
    from tackle.models import Context, JinjaHook


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


def create_jinja_hook(context: 'Context', hook: 'ModelMetaclass') -> 'JinjaHook':
    """Create a jinja hook which is callable via wrapped_exec."""
    from tackle.models import JinjaHook, BaseContext

    return JinjaHook(
        hook=hook,
        context=BaseContext(
            input_context=context.input_context,
            public_context=context.public_context,
            existing_context=context.existing_context,
            no_input=context.no_input,
            calling_directory=context.calling_directory,
            calling_file=context.calling_file,
            public_hooks=context.public_hooks,
            private_hooks=context.private_hooks,
            key_path=context.key_path,
            verbose=context.verbose,
            env_=context.env_,
        ),
    )


def add_jinja_hook_methods(
    context: 'Context',
    jinja_hook: 'JinjaHook',
):
    """Recursively look through hook and add methods to jinja hook so that if"""
    from tackle.parser import create_function_model

    for k, v in jinja_hook.hook.__fields__.items():
        if v.type_ == Callable:
            # Enrich the method with the base attributes
            for i in jinja_hook.hook.__fields__['function_fields'].default:
                # Don't override attributes within the method
                if i not in v.default.function_dict:
                    v.default.function_dict[i] = jinja_hook.hook.__fields__[
                        'function_dict'
                    ].default[i]

            # Build the function with a copy of the dict, so it can be called twice
            # without losing methods
            method_base = create_function_model(
                context=context, func_name=k, func_dict=v.default.function_dict.copy()
            )

            # Create the jinja method with
            jinja_method = create_jinja_hook(context, method_base)

            # Add the jinja method's exec as an attribute of the base's wrapped exec so
            # that it can be called within the jinja globals along with the wrapped exec
            jinja_method.set_method(k, jinja_method.wrapped_exec)

            add_jinja_hook_methods(context, jinja_method)


# wrapped_exec calls exec on the `hook` integrating any positional args
def render_string(context: 'Context', raw: str):
    """
    Render strings by first extracting renderable variables then build a render context
    from the public_context, then existing context, and last looks up special variables.
    After the value has been rendered it is returned as literal so as to preserve the
    original type of the value.

    :return: The literal value if the output is a string / list / dict / float / int
    """
    if ('{{' not in raw) and ('{%' not in raw):
        return raw

    try:
        template = context.env_.from_string(raw)
    except TemplateSyntaxError as e:
        raise MalformedTemplateVariableException(
            str(e).capitalize() + f" in {raw}", context=context
        ) from None

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
            elif 'kwargs' in argments:
                # TODO: This should support callable special vars
                raise NotImplementedError
            else:
                raise ValueError("This should never happen.")
        else:
            unknown_variables.append(v)

    # Evaluate any hooks and insert into jinja environment globals
    if len(unknown_variables) != 0:
        # Unknown variables can be real unknown variables, preloaded jinja globals or
        # hooks which need to be inserted into the global env so that they can be called
        for i in unknown_variables:
            if i in context.public_hooks or i in context.private_hooks:
                hook = get_public_or_private_hook(context, i)

                # Keep track of the hook put in globals so that it can be removed later
                used_hooks.append(i)

                if isinstance(hook, LazyBaseFunction):
                    # In this case the hook was imported from the `hooks` directory and
                    # it needs to be created before being put in the jinja.globals.
                    from tackle.parser import create_function_model

                    hook = create_function_model(
                        context=context,
                        func_name=i,
                        # Copying allows calling hook twice - TODO: carry over arrow
                        func_dict=hook.function_dict.copy(),
                    )

                    # Replace the provider hooks with instantiated function
                    # context.provider_hooks[i] = hook
                    # TODO: carry over arrow to know where to put hook

                # Create the jinja method with
                jinja_hook = create_jinja_hook(context, hook)

                # Iterate recursively through hook fields looking for methods as
                # type Callables and create attributes on their base function so
                # that those methods can be called individually.
                add_jinja_hook_methods(context, jinja_hook)

                # Add the hook to the jinja environment globals along with all hook
                # methods
                context.env_.globals[i] = jinja_hook.wrapped_exec

            else:
                # An error will be thrown later when the variable can't be rendered
                pass
    try:
        rendered_template = template.render(render_context)

        # Need to remove the hook from the globals as if it is called a second time,
        # it is no longer an unknown variable and will use the prior arguments if they
        # have not been re-instantiated.
        for i in used_hooks:
            context.env_.globals.pop(i)

        # # TODO: RM?
        if rendered_template.startswith('<bound method'):
            # Handle unknown variables that are the same as hook_types issues/55
            raise UndefinedError(
                f"A variable `{'/'.join(used_hooks)}` is the same as "
                f"a hook and either not declared as a variable or "
                f"doesn't have arguments. Consider changing."
            )

        # Check for ambiguous globals like `namespace` tackle/issues/19
        match = re.search(r'\<class \'(.+?)\'>', rendered_template)
        if match:
            ambiguous_key = match.group(1).split('.')[-1].lower()
            if ambiguous_key in context.public_context:
                rendered_template = context.public_context[ambiguous_key]
            elif match.group(1) in context.existing_context:
                rendered_template = context.existing_context[ambiguous_key]

    except TypeError as e:
        # Raised when the wrong type is provided to a hook
        # TODO: Consider detecting when StrictUndefined is part of e and raise an
        #  UnknownVariable type of error
        raise UnknownTemplateVariableException(str(e), context=context) from None
    except UndefinedError as e:
        raise UnknownTemplateVariableException(str(e), context=context) from None
    except ValidationError as e:
        # Raised when the wrong type is provided to a hook
        raise MissingTemplateArgsException(str(e), context=context) from None

    # Return the literal type with a few exception handlers
    return literal_eval(rendered_template)
