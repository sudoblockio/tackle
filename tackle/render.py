import re
from inspect import signature
from typing import TYPE_CHECKING, Any, Type

from jinja2 import StrictUndefined, Undefined, meta
from jinja2.exceptions import TemplateSyntaxError, UndefinedError
from pydantic import ValidationError

from tackle import exceptions
from tackle.special_vars import special_variables

if TYPE_CHECKING:
    from tackle import Context
    from tackle.models import BaseHook


def render_variable(context: 'Context', raw: Any):
    """
    Render the raw input. Does recursion with dict and list inputs, otherwise renders
    string.
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
    """
    Take the unknown variables and build a dict used for rendering these variables by
     checking in the various data objects for keys that can be used for rendering.
     Descending priorities = temporary, public, private, existing, special_variables
    """
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
     Used via __call__ method to execute a hook.
    """

    def __init__(self, Hook: Type['BaseHook'], context: 'Context'):
        self.Hook = Hook
        self.context = context

    def __call__(self, *args, **kwargs):
        """Associate any args with kwargs and call the hook."""
        from tackle.parser import evaluate_args, run_hook_exec

        args_list = list(args)
        for i in args_list:
            if isinstance(i, StrictUndefined):
                raise exceptions.TooManyTemplateArgsException(
                    "Too many arguments supplied to hook call", context=self.context
                )
        evaluate_args(
            args=args_list, hook_dict=kwargs, Hook=self.Hook, context=self.context
        )
        hook = self.Hook(**kwargs)
        return run_hook_exec(context=self.context, hook=hook)


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
    from tackle.hooks import get_hooks_from_namespace

    Hook = get_hooks_from_namespace(context=context, hook_name=hook_name)
    if Hook is None:
        return

    # Create a JinjaHook class which will house the Hook and have a __call__ method
    jinja_hook = JinjaHook(Hook=Hook, context=context)

    # Only compile methods for jinja hooks which so happen to have hook_method_set
    # TODO: Clean this up when we wrap hooks with callable classes
    if 'hook_method_set' in Hook.model_fields:
        # Add any methods which could exist but are not known until they are called
        add_jinja_hook_methods(context=context, jinja_hook=jinja_hook)

    # Keep track of the hook put in globals so that it can be removed later
    # because each time you call a hook it could be compiled differently
    used_hooks.append(hook_name)

    # Add the callable hook to the jinja environment globals
    context.env_.globals[hook_name] = jinja_hook


def handle_ambiguous_keys(
    context: 'Context',
    rendered_template: str,
    # used_hooks: list[str],
) -> str:
    """
    After rendering a string, we need to check if the user mistakenly rendered a jinja
     globals callable like `namespace`/`range` or hook without calling it (ie MyHook())
     both of which could be in context.data.*. as a variable. So we check for these
     ambiguous rendering situations here.
    """

    def lookup_ambigous_key(context: 'Context', ambiguous_key: Any):
        if context.data.temporary and ambiguous_key in context.data.temporary:
            return context.data.temporary[ambiguous_key]
        elif ambiguous_key in context.data.public:
            return context.data.public[ambiguous_key]
        elif context.data.private and ambiguous_key in context.data.private:
            return context.data.private[ambiguous_key]
        elif context.data.existing and ambiguous_key in context.data.existing:
            return context.data.existing[ambiguous_key]
        else:
            raise exceptions.UnknownTemplateVariableException(
                f"Unknown ambiguous key {ambiguous_key}. Tracking issue at "
                f"tackle/issues/19",
                context=context,
            ) from None

    if isinstance(rendered_template, type):
        # Handle jinja globals like `namespace` and `range`
        ambiguous_key = rendered_template.__name__
        if rendered_template.__module__ == 'jinja2.utils':
            ambiguous_key = ambiguous_key.lower()
        return lookup_ambigous_key(context, ambiguous_key)
    elif isinstance(rendered_template, JinjaHook):
        # Handle hooks
        hook_name = rendered_template.Hook.hook_name
        raise exceptions.MalformedTemplateVariableException(
            f"Uncalled hook=`{hook_name}` within rendering, try calling "
            f"`{hook_name}()` with args or kwargs.",
            context=context,
        )
    elif isinstance(rendered_template, str):
        if 'jinja2.utils' not in rendered_template:
            return rendered_template
        match = re.search(r"<class 'jinja2\.utils\.(.*?)'>(.*)",
                          rendered_template)
        if match.group(1) in ['Namespace']:
            return lookup_ambigous_key(context, match.group(1).lower()) + match.group(2)

    # if rendered_template.startswith('<tackle.render.JinjaHook object at 0x'):
    #     # Handle unknown variables that are the same as hook_name issues/55
    #     raise UndefinedError(
    #         f"A variable `{'/'.join(used_hooks)}` is the same as a hook and either not"
    #         f" declared as a variable or doesn't have arguments. Consider changing."
    #     )

    # Check for ambiguous globals like `namespace`
    # TODO: tackle/issues/19 -> This is hacky af... Need to redo this with visitor
    # match = re.search(r'\<class \'(.+?)\'>', rendered_template)
    # if match:
    #     ambiguous_key = match.group(1).split('.')[-1].lower()
    #     if context.data.temporary and ambiguous_key in context.data.temporary:
    #         ambiguous_key_rendered = context.temporary_context[ambiguous_key]
    #     elif ambiguous_key in context.data.public:
    #         ambiguous_key_rendered = context.data.public[ambiguous_key]
    #     elif context.data.private and ambiguous_key in context.private_context:
    #         ambiguous_key_rendered = context.data.private[ambiguous_key]
    #     elif context.data.existing and ambiguous_key in context.data.existing:
    #         ambiguous_key_rendered = context.data.existing[ambiguous_key]
    #     else:
    #         raise exceptions.UnknownTemplateVariableException(
    #             f"Unknown ambiguous key {ambiguous_key}. Tracking issue at "
    #             f"tackle/issues/19",
    #             context=context,
    #         ) from None
    #     if isinstance(ambiguous_key_rendered, str):
    #         rendered_template = (
    #                 rendered_template[: match.regs[0][0]]
    #                 + ambiguous_key_rendered
    #                 + rendered_template[match.regs[0][1]:]
    #         )
    #     else:
    #         rendered_template = ambiguous_key_rendered

    return rendered_template


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
                context=context, hook_name=i, used_hooks=used_hooks
            )
    try:
        rendered_template = template.render(render_context)
    except TypeError as e:
        # Raised when the wrong type is provided to a hook
        # TODO: Consider detecting when StrictUndefined is part of e and raise an
        #  UnknownVariable type of error
        raise exceptions.UnknownTemplateVariableException(
            str(e), context=context
        ) from None
    except UndefinedError as e:
        raise exceptions.UnknownTemplateVariableException(
            str(e), context=context
        ) from None
    except ValidationError as e:
        # Raised when the wrong type is provided to a hook
        raise exceptions.MissingTemplateArgsException(str(e), context=context) from None

    # Need to remove the hook from the globals as if it is called a second time,
    # it is no longer an unknown variable and will use the prior arguments if they
    # have not been re-instantiated.
    for i in used_hooks:
        context.env_.globals.pop(i)
    # *Super hacky* function to handle keys that are the same as jinja globals like
    # namespace or range - These could actually be renderable from context.data
    rendered_template = handle_ambiguous_keys(context, rendered_template)
    # *Super hacky* way to deal with malformed types specifically string integers
    # being coerced to integers
    if isinstance(rendered_template, (int, float)):
        if used_hooks or isinstance(rendered_template, bool):  # bools are ints
            pass
        elif len(unknown_variables) == 1:
            if isinstance(render_context[list(unknown_variables)[0]], str):
                rendered_template = str(rendered_template)

    if isinstance(rendered_template, Undefined):
        raise exceptions.UnknownTemplateVariableException(
            f"Could not find one of `{', '.join(unknown_variables)}` in the context, "
            f"Exiting...",
            context=context,
        ) from None

    return rendered_template
