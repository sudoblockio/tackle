import sys
from PyInquirer import prompt

try:
    from rich import pprint
except ImportError:
    from pprint import pprint

from tackle.models import BaseHook


class DebugHook(BaseHook):
    """Hook for debugging that prints the output context and pauses runtime."""

    hook_type: str = 'debug'

    def exec(self) -> None:
        """Run the hook."""
        print("Existing context")
        pprint(dict(self.existing_context))
        print("Local context")
        pprint(dict(self.public_context))
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
