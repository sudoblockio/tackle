# -*- coding: utf-8 -*-

"""Select hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt
from typing import Any, List, Union

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class InquirerListHook(BaseHook):
    """
    Hook for PyInquirer 'list' type prompts.

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

    type: str = 'select'

    index: bool = False
    default: Any = None
    choices: Union[List[str], List[dict]]
    name: str = 'tmp'
    message: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.message:
            self.message = ''.join([self.key, " >> "])

    def execute(self) -> str:
        # Figure out what type of dictionary it is
        choices_type = None
        for i, v in enumerate(self.choices):
            if i != 0 and type(v) != choices_type:
                raise ValueError("All items need to be of the same type")
            choices_type = type(v)

        if choices_type == str:
            answer = self._run_prompt()
            if self.index:
                return self.choices.index(answer)
            else:
                return answer
        elif choices_type == dict:
            choices = []
            for i in self.choices:
                choices.append(i[list(i.keys())[0]])

            choices_dict = self.choices
            self.choices = choices

            answer = self._run_prompt()
            for i in choices_dict:
                val = list(i.keys())[0]
                if i[val] == answer:
                    if self.index:
                        return self.choices.index(answer)
                    else:
                        return val
        else:
            raise ValueError("Choices must be dict with ")

    def _run_prompt(self):
        if not self.no_input:
            question = {
                'type': 'list',
                'name': self.name,
                'message': self.message,
                'choices': self.choices,
            }
            if self.default:
                question.update({'default': self.default})
            response = prompt([question])

            if self.name != 'tmp':
                return response
            else:
                return response['tmp']
        elif self.default:
            return self.default
        elif isinstance(self.choices[0], str):
            return self.choices[0]
        elif isinstance(self.choices[0], dict):
            return list(self.choices[0].keys())[0]
