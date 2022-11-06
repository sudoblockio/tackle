import sys
from InquirerPy import prompt
from pprint import pprint
from rich import print

from tackle import BaseHook, Field


class DebugHook(BaseHook):
    """Hook for debugging that prints the output context and pauses runtime."""

    hook_type: str = 'debug'
    key: str = Field(None, description="A path to a key to debug")
    context: str = Field(
        None,
        description="Which context to examine. One of `public`, `private`, "
        "`temporary`, or `existing`. Omit for all.",
    )

    _contexts: list = ['public', 'private', 'temporary', 'existing']

    def print_key(self, print_context):
        if self.key is not None:
            if self.key in print_context:
                pprint(print_context[self.key])
                return True
            else:
                return False
        else:
            pprint(print_context[self.key])

    def print_context(self, print_context, context_name: str):
        print(f"[bold magenta]{context_name.title()} Context[/bold magenta]")

        # TODO: Improve this -> The builtin pprint is better now since it does the
        #  first level as the top level keys.
        # pretty = Pretty(dict(print_context))
        # panel = Panel(pretty)
        # print(panel)
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
            printed = None
            for i in self._contexts:
                output = getattr(self, f'{i}_context')
                if output is not None and output != {}:
                    if self.key is not None:
                        if self.key in output:
                            self.print_context(output[self.key], i)
                            printed = True
                    else:
                        self.print_context(output, i)
                else:
                    continue

            if self.key is not None and printed is None:
                print(f"Key={self.key} not found in ")

        if not self.no_input:
            question = {
                'type': 'confirm',
                'name': 'tmp',
                'message': 'CONTINUE',
            }
            try:
                response = prompt([question])
            except KeyboardInterrupt:
                print("Exiting...")
                sys.exit(0)

            # Catch keyboard exits with return an empty dict
            if response == {}:
                sys.exit(0)
