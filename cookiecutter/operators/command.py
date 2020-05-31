import sys
from cookiecutter.operators import BaseOperator
import subprocess


class CommandOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'command'

    def __init__(self, operator_dict, context=None):
        """Initialize PyInquirer Hook."""  # noqa
        super(CommandOperator, self).__init__(
            operator_dict=operator_dict, context=context
        )

    def execute(self):
        """Run the prompt."""  # noqa
        p = subprocess.Popen(
            self.operator_dict['command'],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, err = p.communicate()

        if err:
            sys.exit(err)
        return output.decode("utf-8")
