import sys
from pprint import pprint

from InquirerPy import prompt
from rich import print

from tackle import BaseHook, Context, Field, exceptions

DATA_NAMESPACES = ['public', 'private', 'temporary', 'existing']


class DebugHook(BaseHook):
    """Hook for debugging that prints the output data and pauses runtime."""

    hook_name = 'debug'
    key: str | None = Field(None, description="A path to a key to debug")
    data: str = Field(
        None,
        description="Which data to examine. One of `public`, `private`, "
        "`temporary`, or `existing`. Omit for all.",
    )

    skip_output: bool = True
    args: list = ['key']

    def print_key(self, print_data):
        if self.key is not None:
            if self.key in print_data:
                pprint(print_data[self.key])
                return True
            else:
                return False
        else:
            pprint(print_data[self.key])

    def print_data(self, print_data, data_name: str):
        print(f"[bold magenta]{data_name.title()} Data[/bold magenta]")

        # TODO: Improve this -> The builtin pprint is better now since it does the
        #  first level as the top level keys.
        # pretty = Pretty(dict(print_data))
        # panel = Panel(pretty)
        # print(panel)
        pprint(print_data)

    def exec(self, context: 'Context') -> None:
        print(f"Debug at key_path={context.key_path}")
        if self.data is not None:
            if self.data in DATA_NAMESPACES:
                output = getattr(self, f'{self.data}_data')
                if output is not None:
                    self.print_data(output, self.data)
                else:
                    print(f"Debugging {self.data} not possible because it is empty.")
            else:
                print(
                    f"Input data in debug hook `{self.data}` must be one of "
                    f"`public`, `private`, `temporary`, or `existing`"
                )
        else:
            printed = None
            for i in DATA_NAMESPACES:
                output = getattr(context.data, f'{i}')
                if output is not None and output != {}:
                    if self.key is not None:
                        if self.key in output:
                            self.print_data(output[self.key], i)
                            printed = True
                    else:
                        self.print_data(output, i)
                else:
                    continue

            if self.key is not None and printed is None:
                print(f"Key={self.key} not found in ")

        if not context.no_input:
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
            except EOFError:
                raise exceptions.HookCallException(
                    "Prompt run in automation...", context=context
                )

            # Catch keyboard exits with return an empty dict
            if response == {}:
                sys.exit(0)
