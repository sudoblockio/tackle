from PyInquirer import prompt

from cookiecutter.operators import BaseOperator


class InquirerConfirmOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'confirm'

    def __init__(self, operator_dict, context=None):
        """Initialize PyInquirer Hook."""  # noqa
        super(InquirerConfirmOperator, self).__init__(
            operator_dict=operator_dict, context=context
        )

    def execute(self):
        """Run the prompt."""  # noqa
        if 'name' not in self.operator_dict:
            self.operator_dict.update({'name': 'tmp'})
            return prompt([self.operator_dict])['tmp']
        else:
            return prompt([self.operator_dict])
