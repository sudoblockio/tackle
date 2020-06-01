import cookiecutter
from cookiecutter.operators import BaseOperator


class CookiecutterOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'cookiecutter'

    def __init__(self, operator_dict, context=None):
        """Initialize PyInquirer Hook."""  # noqa
        super(CookiecutterOperator, self).__init__(
            operator_dict=operator_dict, context=context
        )

    def execute(self):
        """Run the prompt."""  # noqa

        if 'checkout' in self.operator_dict:
            checkout = self.operator_dict['checkout']
        else:
            checkout = None

        result = cookiecutter.main.cookiecutter(
            template=self.operator_dict['template'], checkout=checkout,
        )

        return result
