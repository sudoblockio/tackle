import sys
from pydantic.main import ModelMetaclass, ModelField, ValidationError
from pydantic import BaseModel
from jinja2 import Template
from typing import Any, List

from tackle import exceptions
from tackle.models import Context
from tackle.hooks import LazyBaseFunction

HELP_TEMPLATE = """usage: tackle {{input_string}} {% for i in general_kwargs %}{{i}} {% endfor %}
{% if general_help %}
{{general_help}}
{% endif %}{% if flags != [] %}
flags:{% for i in flags %}
    --{{i.name}}      {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78) }}{% endif %}{% endfor %}{% endif %}{% if kwargs != [] %}
options:{% for i in kwargs %}
    --{{i.name}} [{{ i.type }}] {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78) }}{% endif %}{% endfor %}{% endif %}{% if args != [] %}
positional arguments:{% for i in args %}
    {{i.name}} [{{ i.type }}] {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78) }}{% endif %}{% endfor %}{% endif %}{% if methods != [] %}
methods:{% for i in methods %}
    {{i.name}}     {% if i.description != None %}{{ ('' ~ i.description) | wordwrap(78) }}{% endif %}{% endfor %}{% endif %}
"""


class HelpInput(BaseModel):
    """Validate help input."""

    name: str
    type: str
    default: Any = None
    description: str = None


def unpack_hook(
    context: 'Context', hook: ModelMetaclass
) -> (List[dict], List[dict], List[dict], List[dict]):
    """Unpack arguments (args/kwargs/flags/methods) from hook."""
    args = []
    kwargs = []
    flags = []
    methods = []

    # kwargs + flags
    for i in hook.__fields__['function_fields'].default.copy():
        # Consume the arg as what is left will be a method which will deal with later
        hook_field = hook.__fields__['function_dict'].default.pop(i)

        # Skip fields that have a `visible=False` field
        if isinstance(hook_field, ModelField):
            # Methods fields are of type ModelField
            # TODO: Determine this logic
            pass
        else:
            if 'visible' in hook_field and not hook_field['visible']:
                continue

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
                hook_name = hook.identifier.split('.')[-1]
                if hook_name == '':  # Default hook
                    hook_name = 'default hook'
                raise exceptions.MalformedFunctionFieldException(
                    f"The field '{i}' is malformed. Getting error=\n{e.__str__()}",
                    context=context,
                    function_name=hook_name,
                ) from None
        elif isinstance(hook_field, ModelField):
            # TODO: https://github.com/robcxyz/tackle/issues/91
            # If enabling inheritance for base vars in to the help, then this will
            # neeed to be active.
            # help_arg = HelpInput(
            #     name=i,
            #     type=hook_field.type_.__name__,
            #     # description=hook_field.d  # TODO: Fix this
            # )
            continue
        else:
            raise NotImplementedError

        if help_arg.type == 'bool':
            flags.append(help_arg.dict())
        else:
            kwargs.append(help_arg.dict())

    # args
    for arg in hook.__fields__['args'].default:
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
                raise exceptions.MalformedFunctionFieldException(
                    "The args don't match a key word arg or flag.",
                    # TODO: Fix
                    function_name=hook.__fields__,
                    context=context,
                ) from None
        args.append(arg_data)

    # methods
    for k, v in hook.__fields__['function_dict'].default.items():
        if k.endswith('<-') and k not in ['exec', 'exec<-']:
            methods.append(
                HelpInput(
                    name=k[:-2],
                    type='method',
                    description=v['help'] if 'help' in v else None,
                ).dict()
            )

    return args, kwargs, flags, methods


def get_methods_on_default_hook(context: 'Context') -> List[dict]:
    """
    When showing help for the default hook, we must show the additional methods. This
    function gets those methods from the context.
    """
    methods = []

    for k, v in context.public_hooks.items():
        # Handle hooks that could be in the `hooks` dir and will not be instantiated
        if isinstance(v, LazyBaseFunction):
            method_help = ''
            if 'help' in v.function_dict:
                method_help = v.function_dict['help']
        else:
            # Normal hook which has been instantiated
            method_help = (
                v.__fields__['function_dict'].default['help']
                if 'help' in v.__fields__['function_dict'].default
                else ''
            )

        methods.append(
            HelpInput(
                name=k,
                type='method',
                description=method_help,
            ).dict()
        )
    return methods


def run_help(context: 'Context', hook: ModelMetaclass = None):
    """
    Print the help screen then exit. Help can be displayed in three different scenarios.
    1. For the base (no args) -> this shows default / other function's help
    2. For a function (len(args) = 1) -> this shows function's help along with its
        associated methods. This is recursive so depends on depth of methods.
    3. For a function's methods (len(args) > 1) -> this drills into methods
    """
    if hook is not None:
        # We have a default hook or method
        general_help = (
            hook.__fields__['function_dict'].default.pop('help')
            if 'help' in hook.__fields__['function_dict'].default
            else None
        )

        args, kwargs, flags, methods = unpack_hook(context, hook)
        hook_name = hook.identifier.split('.')[-1]
    else:
        # Situation where we don't have a default hook or we have not been given an arg
        # to call a specific hook and need to just display all the base's methods
        args, kwargs, flags, methods, general_help = [], [], [], [], ""
        hook_name = ''

    if hook_name == '':  # Default hook
        hook_name = '_default_'
        # Add the additional methods adjacent to the default hook.
        methods += get_methods_on_default_hook(context=context)

    general_kwargs = []
    for i in kwargs + flags:
        # Show the other options outside the default hook
        general_kwargs.append(f"[--{i['name']}]")

    # Remove the `help` str from the `usage` line in help.
    if context.input_string[-4:] == 'help':
        context.input_string = context.input_string[:-4]

    template = Template(HELP_TEMPLATE)
    help_rendered = template.render(
        args=args,
        kwargs=kwargs,
        flags=flags,
        general_help=general_help,
        general_kwargs=general_kwargs,
        input_string=context.input_string,
        methods=methods,
        hook_name=hook_name,
    )
    print(help_rendered)
    sys.exit(0)
