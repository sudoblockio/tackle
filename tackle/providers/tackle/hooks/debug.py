"""Debug hook."""
import logging
from PyInquirer import prompt
from pprint import pprint

from tackle.models import BaseHook


logger = logging.getLogger(__name__)


class DebugHook(BaseHook):
    """Hook for debugging that prints the output context and pauses runtime."""

    hook_type: str = 'debug'

    def execute(self):
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
            prompt([question])
