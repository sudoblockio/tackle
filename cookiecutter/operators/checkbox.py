# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class InquirerCheckboxOperator(BaseOperator):
    """
    Operator for PyInquirer type prompts.

    Takes in three forms of `choices` inputs.
    1. list of string
    2. list of maps with all keys = `name`
    3. list of maps with the key as the output, the value as displayed question

    :param message: String message to show when prompting.
    :param choices: A list of strings or list of k/v pairs per above description
    :param name: A key to insert the output value to. If not provided defaults to
        inserting into parent key
    :param qmark: A marker to select with like 😃
    :return: List of answers
    """

    type = 'checkbox'

    def __init__(self, *args, **kwargs):  # noqa
        super(InquirerCheckboxOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        # Fix the input choices if they don't have the pattern {'name': 'thing'}
        # and are just a list of strings
        if self.no_input:
            output = (
                self.operator_dict['default'] if 'default' in self.operator_dict else []
            )
            return output

        if 'index' not in self.operator_dict:
            self.operator_dict['index'] = False

        choices_type = None
        for i, v in enumerate(self.operator_dict['choices']):
            if i != 0 and type(v) != choices_type:
                raise ValueError("All items need to be of the same type")
            choices_type = type(v)

        if choices_type == str:
            self.operator_dict['choices'] = [
                {'name': x} if isinstance(x, str) else x
                for x in self.operator_dict['choices']
            ]

            answer = self._run_prompt()
            if self.operator_dict['index']:
                return self.operator_dict['choices'].index(answer)
            else:
                return answer

        elif choices_type == dict:
            # This is the normal input to the operator ie
            # choices = ['name': 'stuff', 'name': 'things']
            keys = list(list(i.keys())[0] for i in self.operator_dict['choices'])
            num_keys = list(dict.fromkeys(keys))
            if len(num_keys) == 1 and keys[0] == 'name':
                return self._run_prompt()

            # Otherwise we expect to reindex the key as the output per this:
            # choices = ['stuff': 'How much stuff?', 'things': 'How many things?']
            choices = []
            for i in self.operator_dict['choices']:
                choices.append(i[list(i.keys())[0]])

            # Fixing to the expected input choices {'name': 'stuff', 'name': ...}
            choices_dict = self.operator_dict['choices']
            self.operator_dict['choices'] = [
                {'name': x} if isinstance(x, str) else x for x in choices
            ]

            answer = self._run_prompt()

            # This is for reindexing the output
            output = []
            for i, v in enumerate(choices_dict):
                val = list(v.keys())[0]
                if v[val] in answer:
                    if self.operator_dict['index']:
                        output.append(i)
                    else:
                        output.append(val)
            return output

    def _run_prompt(self):
        if 'name' not in self.operator_dict:
            self.operator_dict.update({'name': 'tmp'})
            return prompt([self.operator_dict])['tmp']
        else:
            return prompt([self.operator_dict])
