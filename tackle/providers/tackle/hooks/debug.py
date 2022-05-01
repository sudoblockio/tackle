import sys
from PyInquirer import prompt

from tackle import BaseHook, Field

rich_install = False
try:
    from pprint import pprint

    from rich import print

    # from rich.pretty import pprint
    # from rich.pretty import Pretty
    # from rich.panel import Panel
    rich_install = True
except ImportError:
    from pprint import pprint


class DebugHook(BaseHook):
    """Hook for debugging that prints the output context and pauses runtime."""

    hook_type: str = 'debug'
    context: str = Field(
        None,
        description="Which context to examine. One of `public`, `private`, "
        "`temporary`, or `existing`. Omit for all.",
    )

    _contexts: list = ['public', 'private', 'temporary', 'existing']

    def print_context(self, print_context, context_name: str):
        if rich_install:
            print(f"[bold magenta]{context_name.title()} Context[/bold magenta]")

            # TODO: Improve this -> The builtin pprint is better now since it does the
            #  first level as the top level keys.
            # pretty = Pretty(dict(print_context))
            # panel = Panel(pretty)
            # print(panel)
            pprint(print_context)

        else:
            print(f"{context_name.title()} Context")
            pprint(print_context)

    def exec(self) -> None:
        if self.context is not None:
            if self.context in self._contexts:
                output = getattr(self, f'{self.context}_context')
                if output is not None:
                    self.print_context(output, self.context)
                else:
                    print(f"Debugging {self.context} not possible because it is empty.")
            else:
                print(
                    f"Input context in debug hook `{self.context}` must be one of "
                    f"`public`, `private`, `temporary`, or `existing`"
                )
        else:
            for i in self._contexts:
                output = getattr(self, f'{i}_context')
                if output is not None and output != {}:
                    self.print_context(output, i)
                else:
                    continue

        if not self.no_input:
            question = {
                'type': 'confirm',
                'name': 'tmp',
                'message': 'CONTINUE',
            }
            response = prompt([question])

            # Catch keyboard exits with return an empty dict
            if response == {}:
                sys.exit(0)
