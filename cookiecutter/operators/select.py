# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class InquirerListOperator(BaseOperator):
    """
    Operator for PyInquirer 'list' type prompts.

    Takes in two forms of `choices` inputs.
    1. list of string
    2. list of maps with the key as the output, the value as displayed question

    :param message: String message to show when prompting.
    :param choices: A list of strings or list of k/v pairs per above description
    :param name: A key to insert the output value to. If not provided defaults to
        inserting into parent key
    :param index: Boolean to return the index instead of the answer
    :return: String for answer
    """

    type = 'select'

    def __init__(self, *args, **kwargs):  # noqa
        super(InquirerListOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        # Fix type
        self.operator_dict['type'] = 'list'

        if 'index' not in self.operator_dict:
            self.operator_dict['index'] = False

        if self.no_input:
            if 'default' in self.operator_dict:
                return self.operator_dict['default']
            else:
                return None

        # Figure out what type of dictionary it is
        choices_type = None
        for i, v in enumerate(self.operator_dict['choices']):
            if i != 0 and type(v) != choices_type:
                raise ValueError("All items need to be of the same type")
            choices_type = type(v)

        # if isinstance(self.operator_dict['choices'], list):
        if choices_type == str:
            answer = self._run_prompt()
            if self.operator_dict['index']:
                return self.operator_dict['choices'].index(answer)
            else:
                return answer
        elif choices_type == dict:
            choices = []
            for i in self.operator_dict['choices']:
                choices.append(i[list(i.keys())[0]])

            choices_dict = self.operator_dict['choices']
            self.operator_dict['choices'] = choices

            answer = self._run_prompt()
            for i in choices_dict:
                val = list(i.keys())[0]
                if i[val] == answer:
                    if self.operator_dict['index']:
                        return self.operator_dict['choices'].index(answer)
                    else:
                        return val
        else:
            raise ValueError("Choices must be dict with ")

    def _run_prompt(self):
        if 'name' not in self.operator_dict:
            self.operator_dict.update({'name': 'tmp'})
            return prompt([self.operator_dict])['tmp']
        else:
            return prompt([self.operator_dict])
