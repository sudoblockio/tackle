"""Debug hook."""
import logging
from PyInquirer import prompt
from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class DebugHook(BaseHook):
    """Hook for debugging that prints the output context and pauses runtime."""

    hook_type: str = 'debug'

    def execute(self):
        """Run the hook."""
        print(dict(self.output_dict))
        if not self.no_input:
            question = {
                'type': 'confirm',
                'name': 'tmp',
                'message': 'CONTINUE',
            }
            prompt([question])
