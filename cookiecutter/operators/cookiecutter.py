# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals
from __future__ import print_function

import cookiecutter
import logging

from cookiecutter.operators import BaseOperator


logger = logging.getLogger(__name__)


class CookiecutterOperator(BaseOperator):
    """Operator for calling external cookiecutters."""

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
            template=self.operator_dict['template'], checkout=checkout
        )  # noqa

        return result


class CookiecutterPromptOperator(BaseOperator):
    """Operator for cookiecutter type prompts."""

    type = 'cookiecutter_prompt'

    def __init__(self, operator_dict, context=None):
        """Initialize PyInquirer Hook."""  # noqa
        super(CookiecutterPromptOperator, self).__init__(
            operator_dict=operator_dict, context=context
        )

    def execute(self):
        """Run the prompt."""  # noqa

        if 'no_input' in self.operator_dict:
            no_input = self.operator_dict['no_input']
        else:
            no_input = False

        if 'template' in self.operator_dict:
            context = cookiecutter.utils.read_config_file(
                self.operator_dict['template']
            )  # noqa
        else:
            context = self.operator_dict['context']

        return cookiecutter.prompt_for_config.cookiecutter(
            context=context, no_input=no_input
        )  # noqa
