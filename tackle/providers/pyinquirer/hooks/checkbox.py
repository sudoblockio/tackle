"""Checkbox hook."""
import logging
from PyInquirer import prompt
from typing import Union, List, Any, Dict
from pydantic import Field

from tackle.models import BaseHook
from tackle.utils.dicts import get_readable_key_path

logger = logging.getLogger(__name__)


class InquirerCheckboxHook(BaseHook):
    """
    Hook for PyInquirer type prompts.

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

    hook_type: str = 'checkbox'

    message: str = Field(None, description="String message to show when prompting.")
    index: bool = Field(
        False, description="Boolean to return the output in a list."
    )  # TODO: Fix this?
    default: Any = Field([], description="Default for the return value")
    choices: Union[List[str], List[Dict]] = Field(
        ..., description="Either a list of strings or dictionary ."
    )
    checked: bool = Field(
        False, description="Boolean if the default choices should all be checked."
    )
    name: str = 'tmp'

    _args: list = ['message']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.message is None:
            self.message = get_readable_key_path(self.key_path_) + ' >>>'

    def execute(self) -> list:
        if self.no_input:
            return self.default

        choices_type = None
        for i, v in enumerate(self.choices):
            if i != 0 and type(v) != choices_type:
                raise ValueError("All items need to be of the same type")
            choices_type = type(v)

        if choices_type == str:
            self.choices = [
                {'name': x} if isinstance(x, str) else x for x in self.choices
            ]

            answer = self._run_prompt()
            # if self.index:
            #     return self.choices.index(answer)
            # else:
            return answer

        elif choices_type == dict:
            # This is the normal input to the Hook ie
            # choices = ['name': 'stuff', 'name': 'things']
            keys = list(list(i.keys())[0] for i in self.choices)
            num_keys = list(dict.fromkeys(keys))
            if len(num_keys) == 1 and keys[0] == 'name':
                return self._run_prompt()

            # Otherwise we expect to reindex the key as the output per this:
            # choices = ['stuff': 'How much stuff?', 'things': 'How many things?']
            choices = []
            for i in self.choices:
                choices.append(i[list(i.keys())[0]])

            # Fixing to the expected input choices {'name': 'stuff', 'name': ...}
            choices_dict = self.choices
            self.choices = [{'name': x} if isinstance(x, str) else x for x in choices]

            answer = self._run_prompt()

            # This is for reindexing the output
            output = []
            for i, v in enumerate(choices_dict):
                val = list(v.keys())[0]
                if v[val] in answer:
                    if self.index:
                        output.append(i)
                    else:
                        output.append(val)
            return output

    def _run_prompt(self):
        question = {
            'type': 'checkbox',
            'name': self.name,
            'message': self.message,
            'choices': self.choices,
            'checked': self.checked,
        }
        if self.default:
            question.update({'default': self.default})
        response = prompt([question])

        if self.name != 'tmp':
            return response
        else:
            return response['tmp']
