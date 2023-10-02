from types import MethodType
import re
from jinja2 import meta, StrictUndefined
from jinja2.exceptions import UndefinedError, TemplateSyntaxError
from inspect import signature
from typing import TYPE_CHECKING, Any
from pydantic import ValidationError

from tackle import exceptions
from tackle.special_vars import special_variables
from tackle.utils.command import literal_eval

if TYPE_CHECKING:
    from typing import Type
    from tackle.models import Context, BaseHook


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

def _wrapped_exec(Hook: 'Type[BaseHook]', *args, **kwargs):
    """
    Function that is temporarily inserted into jinja globals so that it is callable
     when rendering a hook in a jinja template. At this point the uninstantiated hook
     will have a context object on it which is not normal
    """
    from tackle.parser import evaluate_args

    args_list = list(args)
    for i in args_list:
        # TODO: RM?
        if isinstance(i, StrictUndefined):
            raise exceptions.TooManyTemplateArgsException(
                "Too many arguments supplied to hook call",
                context=Hook.context
            )
    evaluate_args(
        args=args_list,
        hook_dict=kwargs,
        Hook=Hook,
        context=Hook.context
    )

    hook = Hook(
        context=Hook.context,
        no_input=Hook.model_fields['no_input'].default | Hook.context.no_input,
        **kwargs,
    )
    return hook.exec()


# wrapped_exec calls exec on the `hook` integrating any positional args
def render_string(context: 'Context', raw: str) -> Any:
    """
    Render strings by first extracting renderable variables then build a render context
     from the public_context, then existing context, and last looks up special
     variables. After the value has been rendered it is returned as literal so as to
     preserve the original type of the value.

    :return: The literal value if the output is a string / list / dict / float / int
    """
    if not isinstance(raw, str):
        return raw

    if ('{{' not in raw) and ('{%' not in raw):
        return raw

    try:
        # TODO: Parse out filters based on `|`, check if the filter exists in the env,
        #  if not, then compile the hook so that it is callable.
        #  https://github.com/sudoblockio/tackle/issues/85
        template = context.env_.from_string(raw)
    except TemplateSyntaxError as e:
        raise exceptions.MalformedTemplateVariableException(
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
        if context.data.temporary and v in context.data.temporary:
            render_context.update({v: context.data.temporary[v]})
        elif context.data.public and v in context.data.public:
            render_context.update({v: context.data.public[v]})
        elif context.data.private and v in context.data.private:
            render_context.update({v: context.data.private[v]})
        elif context.data.existing and v in context.data.existing:
            render_context.update({v: context.data.existing[v]})
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
                raise Exception("This should never happen...")
        else:
            unknown_variables.append(v)

    # Evaluate any hooks and insert into jinja environment globals
    if len(unknown_variables) != 0:
        # Unknown variables can be real unknown variables, preloaded jinja globals or
        # hooks which need to be inserted into the global env so that they can be called
        for i in unknown_variables:
            # TODO: We probably need to split here for methods

            if i in context.hooks.public or i in context.hooks.private:
                from tackle.hooks import get_public_or_private_hook, create_dcl_hook

                Hook = get_public_or_private_hook(context, i)

                # Keep track of the hook put in globals so that it can be removed later
                used_hooks.append(i)

                # Add context to Hook which is later reinstantiated in _wrapped_exec
                # Prior attempts at this used a partial which threw an error in jinja
                # when using args since jinja uses a `context` property which then
                # threw a duplicate input variable exception to the callable
                Hook.context = context
                Hook.wrapped_exec = MethodType(_wrapped_exec, Hook)

                # Old version kept for posterity
                # _wrapped_exec_with_context = partial(_wrapped_exec, context=context)
                # Hook.wrapped_exec = MethodType(_wrapped_exec_with_context, Hook)

                # Iterate recursively through hook fields looking for methods as
                # type Callables and create attributes on their base function so
                # that those methods can be called individually.
                # add_jinja_hook_methods(context, jinja_hook)

                # Add the callable hook to the jinja environment globals
                context.env_.globals[i] = Hook.wrapped_exec
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

        # TODO: RM?
        if rendered_template.startswith('<bound method'):
            # Handle unknown variables that are the same as hook_types issues/55
            raise UndefinedError(
                f"A variable `{'/'.join(used_hooks)}` is the same as "
                f"a hook and either not declared as a variable or "
                f"doesn't have arguments. Consider changing."
            )

        # Check for ambiguous globals like `namespace`
        # TODO: tackle/issues/19 -> This is hacky af... Need to redo this with visitor
        match = re.search(r'\<class \'(.+?)\'>', rendered_template)
        if match:
            ambiguous_key = match.group(1).split('.')[-1].lower()
            if context.temporary_context and ambiguous_key in context.temporary_context:
                ambiguous_key_rendered = context.temporary_context[ambiguous_key]
            elif ambiguous_key in context.public_context:
                ambiguous_key_rendered = context.public_context[ambiguous_key]
            elif context.private_context and ambiguous_key in context.private_context:
                ambiguous_key_rendered = context.private_context[ambiguous_key]
            elif context.existing_context and ambiguous_key in context.existing_context:
                ambiguous_key_rendered = context.existing_context[ambiguous_key]
            else:
                raise exceptions.UnknownTemplateVariableException(
                    f"Unknown ambiguous key {ambiguous_key}. Tracking issue at "
                    f"tackle/issues/19",
                    context=context,
                ) from None
            if isinstance(ambiguous_key_rendered, str):
                rendered_template = (
                    rendered_template[: match.regs[0][0]]
                    + ambiguous_key_rendered
                    + rendered_template[match.regs[0][1] :]
                )
            else:
                rendered_template = ambiguous_key_rendered

    except TypeError as e:
        # Raised when the wrong type is provided to a hook
        # TODO: Consider detecting when StrictUndefined is part of e and raise an
        #  UnknownVariable type of error
        raise exceptions.UnknownTemplateVariableException(str(e), context=context) from None
    except UndefinedError as e:
        raise exceptions.UnknownTemplateVariableException(str(e), context=context) from None
    except ValidationError as e:
        # Raised when the wrong type is provided to a hook
        raise exceptions.MissingTemplateArgsException(str(e), context=context) from None

    # Return the literal type with a few exception handlers
    return literal_eval(rendered_template)
