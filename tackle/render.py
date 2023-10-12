import re
from inspect import signature
from jinja2 import meta, StrictUndefined
from jinja2.exceptions import UndefinedError, TemplateSyntaxError
from typing import TYPE_CHECKING, Any
from pydantic import ValidationError

from tackle import exceptions
from tackle.special_vars import special_variables
from tackle.utils.command import literal_eval

if TYPE_CHECKING:
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
        return render_string(context=context, raw=raw)
    elif isinstance(raw, dict):
        return {
            render_string(context, k): render_variable(context, v)
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return [render_variable(context, v) for v in raw]
    else:
        return raw


def create_render_context(
        context: 'Context',
        variables: set[str],
) -> (dict, list[str]):
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
    return render_context, variables


class JinjaHook:
    """
    Object to temporarily place inside jinja.globals that can be called when rendering.
     I
    """

    def __init__(self, Hook: 'BaseHook', context: 'Context'):
        self.Hook = Hook
        self.context = context

    def __call__(self, *args, **kwargs):
        """Associate any args with kwargs and call the hook."""
        from tackle.parser import evaluate_args

        args_list = list(args)
        for i in args_list:
            if isinstance(i, StrictUndefined):
                raise exceptions.TooManyTemplateArgsException(
                    "Too many arguments supplied to hook call",
                    context=self.context
                )
        evaluate_args(
            args=args_list,
            hook_dict=kwargs,
            Hook=self.Hook,
            context=self.context
        )

        # no_input is any true value from either hook, context, or kwarg
        no_input = (
            self.Hook.model_fields['no_input'].default |
            self.context.no_input |
            kwargs.pop('no_input') if 'no_input' in kwargs else False
        )

        # TODO: Why is there a type error here?
        # TODO: RM context for inspecting func sig or context
        hook = self.Hook(
            no_input=no_input,
            context=self.context,
            **kwargs,
        )
        return hook.exec()


def add_jinja_hook_methods(context: 'Context', jinja_hook: JinjaHook):
    """
    Recursively compile methods (fields of type Callable) on a hook so that they can be
     callable in jinja.
    """
    from tackle.hooks import create_dcl_method

    for k in jinja_hook.Hook.model_fields['hook_method_set'].default:
        # Compile the method with the hook
        HookMethod = create_dcl_method(context=context, Hook=jinja_hook.Hook, arg=k)

        # Instantiate JinjaHook with the HookMethod
        jinja_method = JinjaHook(Hook=HookMethod, context=context)

        # Add the jinja_method as a callable attribute to jinja_hook thereby adding the
        # method to the base class
        setattr(jinja_hook, k, jinja_method)

        # Recurse for any embedded methods
        add_jinja_hook_methods(context=context, jinja_hook=jinja_method)


def add_jinja_hook_to_jinja_globals(
        context: 'Context',
        hook_name: str,
        used_hooks: list[str],
):
    """Add any unknown variables that are the same as hooks to the jinja globals."""
    if hook_name in context.hooks.public or hook_name in context.hooks.private:
        from tackle.hooks import get_public_or_private_hook, create_dcl_hook, get_hook

        Hook = get_public_or_private_hook(context=context, hook_name=hook_name)

        # Create a JinjaHook class which will house the Hook and have a __call__ method
        jinja_hook = JinjaHook(Hook=Hook, context=context)

        # Add any methods which could exist but are not known until they are called
        add_jinja_hook_methods(context=context, jinja_hook=jinja_hook)

        # Keep track of the hook put in globals so that it can be removed later
        # because each time you call a hook it could be compiled differently
        used_hooks.append(hook_name)

        # Add the callable hook to the jinja environment globals
        context.env_.globals[hook_name] = jinja_hook


def render_string(context: 'Context', raw: str) -> Any:
    """
    Render strings by first extracting renderable variables then build a render context
     from the public_context, then existing context, and last looks up special
     variables. After the value has been rendered it is returned as literal so as to
     preserve the original type of the value.

    :return: The literal value if the output is a string / list / dict / float / int
    """
    if not isinstance(raw, str):
        # We only render strings
        return raw

    if ('{{' not in raw) and ('{%' not in raw):
        # Just check if there are any jinja markers and if not return
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

    # Create a render_context (dict) from variables and return any unknown_variables
    # which will be hooks. Any left over variables will throw error in rendering
    render_context, unknown_variables = create_render_context(context, variables)

    # We need to make a list of used hooks so that we can remove them from the jinja
    # environment's globals later since they should be recompiled as they are mutable
    used_hooks = []

    # Evaluate any hooks and insert into jinja environment globals
    if len(unknown_variables) != 0:
        # Unknown variables can be real unknown variables, preloaded jinja globals or
        # hooks which need to be inserted into the global env so that they can be called
        # Note that only the base of a callable is output as an unknown variable
        # ie {{base.method()}} -> only `base` is in unknown_variables
        for i in unknown_variables:
            add_jinja_hook_to_jinja_globals(
                context=context,
                hook_name=i,
                used_hooks=used_hooks
            )
    try:
        rendered_template = template.render(render_context)

        # Need to remove the hook from the globals as if it is called a second time,
        # it is no longer an unknown variable and will use the prior arguments if they
        # have not been re-instantiated.
        for i in used_hooks:
            context.env_.globals.pop(i)

        # TODO: RM?
        if rendered_template.startswith('<bound method'):
            # Handle unknown variables that are the same as hook_name issues/55
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
                        + rendered_template[match.regs[0][1]:]
                )
            else:
                rendered_template = ambiguous_key_rendered

    except TypeError as e:
        # Raised when the wrong type is provided to a hook
        # TODO: Consider detecting when StrictUndefined is part of e and raise an
        #  UnknownVariable type of error
        raise exceptions.UnknownTemplateVariableException(str(e),
                                                          context=context) from None
    except UndefinedError as e:
        raise exceptions.UnknownTemplateVariableException(str(e),
                                                          context=context) from None
    except ValidationError as e:
        # Raised when the wrong type is provided to a hook
        raise exceptions.MissingTemplateArgsException(str(e), context=context) from None

    # Return the literal type with a few exception handlers
    return literal_eval(rendered_template)
