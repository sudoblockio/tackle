import sys

from tackle.models import Context


HELP_TEMPLATE = """
usage: tackle {{ input_string }}

{% if positional_arguments is not None %}positional arguments:
  {% for i in positional_arguments %}

{% endfor %}{% endif %}

{% if positional_arguments is not None %}optional arguments:
  {% for i in optional_arguments %}

{% endfor %}{% endif %}
"""


def find_help_functions(context: 'Context', args: list):

    # if len(args) == 0:
    #     context.provider_hooks =

    for arg in args:
        if arg in context.context_functions:

            h = context.provider_hooks[arg]
            context.context_functions = ""
    print()


def run_help(context: 'Context', args: list):
    """
    Print the help screen then exit. Help can be displayed in three different scenarios.
    1. For the base (no args) -> this shows all the different function's help
    2. For a function (len(args) = 1) -> this shows function's help along with its
        associated methods. This is recursive so depends on depth of methods.
    3. For a function's methods (len(args) > 1) -> this drills into methods
    """
    find_help_functions(context, args)
    help = [context.provider_hooks[i] for i in context.context_functions]
    for arg in args:
        if arg in context.context_functions:
            context.context_functions

    if len(args) >= 1:
        context.context_functions = [args.pop(0)]

    if len(args) != 0:
        # We need to drill down into methods
        raise NotImplementedError

    help_msg = []
    for i in context.context_functions:
        hook_fields = context.provider_hooks[i].__fields__

        if hook_fields['help'].default is None:
            continue

        help_msg.append(context.provider_hooks[i])
        x = context.provider_hooks[i]
        z = context.provider_hooks[i].__fields__
        print()

    print()
    sys.exit(0)

    # if len(args) == 0:
    #     help_functions = context.context_functions
    # else:
    #     for i, v in enumerate(args):
    #         if i == 0:
    #             if v not in context.context_functions:
    #                 print(
    #                     f"Help for {v} not available, declarative hook not in context.")
    #                 sys.exit(0)
    #         help_functions = [args.pop(0)]
    #
    # # if len(args) >= 0:
    # for i, v in enumerate(args):
    #     # Drill into functions

    # if len(args) >= 1:
    #     # We have been asked for help on a function in the tackle file. Check if it
    #     # exists and then drill into that func and then it's methods if len(args) > 1
    #     # if
    #
    #     # for i in args:
    #     #     if i in
    #     pass
