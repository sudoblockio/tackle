# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import hcl
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator
from cookiecutter.exceptions import EscapeOperatorException

logger = logging.getLogger(__name__)


class TerraformVariablesOperator(BaseOperator):
    """Operator for printing an input and returning the output."""

    type = 'terraform_variables'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(TerraformVariablesOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Read the variables file and prompt user to fill in then return output."""
        with open(self.operator_dict['variables_file'], 'r') as f:
            vars = hcl.load(f)

        var_skip_list = (
            self.operator_dict['var_skip_list']
            if 'var_skip_list' in self.operator_dict
            else []
        )
        output = {}
        for v in (
            vars['variable'].keys()
            if 'var_list' not in self.operator_dict
            else self.operator_dict['var_list']
        ):
            logger.debug('Parsing %s variable', v)

            var = vars['variable'][v]

            description = (
                f"\nDescription - {var['description']}" if 'description' in var else ""
            )
            message = f'What do you want to set the variable "{v}" {description}'

            if 'type' in var:
                if var['type'] in ['bool', 'boolean'] and v not in var_skip_list:
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'confirm',
                        'default': var['default'] if 'default' in var else True,
                        'message': message,
                        'name': v,
                    }
                    output = self._run_prompt(question, output, v)

                if var['type'] in ['string'] and v not in var_skip_list:
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'input',
                        'default': var['default'] if 'default' in var else None,
                        'message': message,
                        'name': v,
                    }
                    output = self._run_prompt(question, output, v)

                if (
                    var['type'] in ['list', 'list(string)', 'list(map(string))']
                    and v not in var_skip_list
                ):
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'checkbox',
                        'default': var['default'] if 'default' in var else None,
                        'message': message,
                        'choices': '',
                        'name': v,
                    }
                    logger.debug('Variable type %s', var['type'])

                    output = self._run_prompt(question, output, v)

                if var['type'] in ['map', 'map(string)'] and v not in var_skip_list:
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'checkbox',
                        'default': var['default'] if 'default' in var else None,
                        'message': message,
                        'name': v,
                    }
                    output = self._run_prompt(question, output, v)

            # if 'type' not in var and v not in var_skip_list:
            #     pprint(var)

        return output

    @staticmethod
    def _run_prompt(question, output, v, var_type=None):
        question.update({'name': 'tmp'})
        answer = prompt([question])['tmp']
        if not isinstance(var_type, dict):
            if answer == {}:
                raise EscapeOperatorException("Process has been cancelled by user.")
        output.update({v: answer})
        return output
