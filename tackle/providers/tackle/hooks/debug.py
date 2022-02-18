import sys
from PyInquirer import prompt
from pprint import pprint

from tackle.models import BaseHook


class DebugHook(BaseHook):
    """Hook for debugging that prints the output context and pauses runtime."""

    hook_type: str = 'debug'

    def execute(self) -> None:
        """Run the hook."""
        print("Existing context")
        pprint(dict(self.existing_context))
        print("Local context")
        pprint(dict(self.output_dict))
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
