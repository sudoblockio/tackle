import sys
from typing import Any, List, Type

from jinja2 import Template
from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo

from tackle import exceptions
from tackle.context import Context
from tackle.models import BaseHook, LazyBaseHook, CompiledHookType
from tackle.utils.type_strings import field_to_string

HELP_TEMPLATE = """usage: tackle {{input_string}} {% for i in general_kwargs %}{{i}} {% endfor %}
{% if general_help %}
{{general_help}}
{% endif %}{% if flags != [] %}
flags:{% for i in flags %}
    --{{i.name.ljust(max_name_length)}} {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78 - max_name_length - 4) }}{% endif %}{% endfor %}{% endif %}{% if kwargs != [] %}
options:{% for i in kwargs %}
    --{{i.name.ljust(max_name_length)}} [{{ i.type }}] {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78 - max_name_length - 4) }}{% endif %}{% endfor %}{% endif %}{% if args != [] %}
positional arguments:{% for i in args %}
    {{i.name.ljust(max_name_length)}} [{{ i.type }}] {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78 - max_name_length - 4) }}{% endif %}{% endfor %}{% endif %}{% if methods != [] %}
methods:{% for i in methods %}
    {{i.name.ljust(max_name_length)}} {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78 - max_name_length - 4) }}{% endif %}{% endfor %}{% endif %}
"""


class HelpInput(BaseModel):
    """Validate help input."""

    name: str
    type: str
    default: Any = None
    description: str | None = None


def unpack_hook(
    context: 'Context',
    Hook: Type[BaseModel],
) -> (List[dict], List[dict], List[dict], List[dict]):
    """Unpack arguments (args/kwargs/flags/methods) from hook."""
    args = []
    kwargs = []
    flags = []
    methods = []

    # kwargs + flags
    for i in Hook.model_fields['hook_field_set'].default.copy():
        # Consume the arg as what is left will be a method which will deal with later
        hook_field = Hook.model_fields[i]

        # TODO: Skip fields marked with `visible`?

        # Serialize help input
        if isinstance(hook_field, str):
            help_arg = HelpInput(
                name=i, type=type(hook_field).__name__, default=hook_field
            )
        elif isinstance(hook_field, dict):
            if 'type' not in hook_field:
                hook_field['type'] = "unknown"
            try:
                help_arg = HelpInput(name=i, **hook_field)
            except ValidationError as e:
                hook_name = Hook.identifier.split('.')[-1]
                if hook_name == '':  # Default hook
                    hook_name = 'default hook'
                raise exceptions.MalformedHookFieldException(
                    f"The field '{i}' is malformed. Getting error=\n{e.__str__()}",
                    context=context,
                    hook_name=hook_name,
                ) from None
        elif isinstance(hook_field, FieldInfo):
            help_arg = HelpInput(
                name=i,
                type=field_to_string(hook_field),
                description=hook_field.description,
            )
        else:
            raise NotImplementedError

        if help_arg.type == 'bool':
            flags.append(help_arg.__dict__)
        else:
            kwargs.append(help_arg.__dict__)

    # args
    for arg in Hook.model_fields['args'].default:
        # Check kwargs
        arg_data = [i for i in kwargs if i['name'] == arg]
        if len(arg_data) == 1:
            arg_data = arg_data[0]
        else:
            # Check flags
            arg_data = [i for i in flags if i['name'] == arg]
            if len(arg_data) == 1:
                arg_data = arg_data[0]
            else:
                raise exceptions.MalformedHookFieldException(
                    "The args don't match a key word arg or flag.",
                    # TODO: Fix
                    hook_name=Hook.model_fields,
                    context=context,
                ) from None
        args.append(arg_data)

    # methods
    for method_name in Hook.model_fields['hook_method_set'].default:
        method = Hook.model_fields[method_name].default.input_raw
        methods.append(
            HelpInput(
                name=method_name,
                type='method',
                description=method['help'] if 'help' in method else None,
            ).__dict__
        )

    return args, kwargs, flags, methods


def get_methods_on_default_hook(context: 'Context') -> List[dict]:
    """
    When showing help at the base for both default and non-hook calls (ie just `help`,
     we must show additional methods. This function gets those methods from the context.
    """
    methods = []

    for k, v in context.hooks.public.items():
        # Handle hooks that could be in the `hooks` dir and will not be instantiated
        if isinstance(v, LazyBaseHook):
            method_help = ''
            if 'help' in v.input_raw:
                method_help = v.input_raw['help']
        else:
            # Normal hook which has been instantiated
            method_help = v.model_fields['help'].default
            if method_help is None:
                method_help = ''

        methods.append(
            HelpInput(
                name=k,
                type='method',
                description=method_help,
            ).__dict__
        )
    return methods


def run_help(context: 'Context', Hook: CompiledHookType = None):
    """
    Print the help screen then exit. Help can be displayed in three different scenarios.
    1. For the base (no args) -> this shows default / other function's help
    2. For a function (len(args) = 1) -> this shows function's help along with its
        associated methods. This is recursive so depends on depth of methods.
    3. For a function's methods (len(args) > 1) -> this drills into methods
    """
    if Hook is not None:
        # We have a default hook or method
        general_help = Hook.model_fields.pop('help').default

        # Unpack the arguments from the hook
        args, kwargs, flags, methods = unpack_hook(context, Hook)
        hook_name = Hook.hook_name
        if hook_name == '_default':  # Default hook
            hook_name = 'default'
            # Add the additional methods adjacent to the default hook.
            methods += get_methods_on_default_hook(context=context)
    else:
        # Situation where we don't have a default hook or we have not been given an arg
        # to call a specific hook and need to just display all the base's methods
        args, kwargs, flags, general_help = [], [], [], ""
        methods = get_methods_on_default_hook(context=context)
        hook_name = ''

    general_kwargs = []
    for i in kwargs + flags:
        # Show the other options outside the default hook
        general_kwargs.append(f"[--{i['name']}]")

    # Determine max width of each kwarg / arg / method for formatting
    max_arg_name_length = max([len(arg['name']) for arg in args], default=0)
    max_kwarg_name_length = max([len(kwarg['name']) for kwarg in kwargs], default=0)
    max_flag_name_length = max([len(flag['name']) for flag in flags], default=0)
    max_method_name_length = max([len(method['name']) for method in methods], default=0)

    # Calculate overall max width for alignment
    max_name_length = (
        max(
            max_arg_name_length,
            max_kwarg_name_length,
            max_flag_name_length,
            max_method_name_length,
        )
        + 2
    )

    template = Template(HELP_TEMPLATE)
    help_rendered = template.render(
        args=args,
        kwargs=kwargs,
        flags=flags,
        general_help=general_help,
        general_kwargs=general_kwargs,
        input_string=context.input.help_string,
        methods=methods,
        hook_name=hook_name,
        max_name_length=max_name_length,
    )
    print(help_rendered)
    sys.exit(0)
