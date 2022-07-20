import sys
from InquirerPy import prompt
from InquirerPy.base.control import Choice

from typing import Union, List, Dict

from tackle.models import BaseHook, Field
from tackle.utils.dicts import get_readable_key_path


class InquirerCheckboxHook(BaseHook):
    """
    Hook for PyInquirer `checkbox` type prompts. Allows the user to multi-select from a
     list of choices and outputs a list. Takes in three forms of `choices` inputs. A
     list of string, a list of maps with all keys having a `name` field per the original
     [spec](https://github.com/CITGuru/PyInquirer/blob/master/examples/checkbox.py), or
     list of maps with the key as the question, the value as the output.
    """

    hook_type: str = 'checkbox'

    message: str = Field(None, description="String message to show when prompting.")
    # default: Any = Field([], description="Default for the return value")
    choices: Union[List[str], List[Dict]] = Field(
        ...,
        description="Either a list of strings or dictionary .",
        render_by_default=True,
    )
    checked: bool = Field(
        False, description="Boolean if the default choices should all be checked."
    )
    index: bool = Field(
        False, description="Boolean to return the index instead of the answer"
    )
    fuzzy: bool = Field(
        False,
        description="Allow fuzzy search like fzf - [docs](https://inquirerpy.readthedocs.io/en/latest/pages/prompts/fuzzy.html)",
    )

    args: list = ['message']
    _docs_order: int = 2

    def exec(self) -> list:
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

        choices_type = None
        for i, v in enumerate(self.choices):
            if i != 0 and type(v) != choices_type:
                raise ValueError("All items need to be of the same type")
            choices_type = type(v)

        if choices_type == str:
            if self.no_input:
                if self.checked:
                    return self.choices
                return []

            choice_list = self.choices.copy()
            self.choices = [
                {'name': x, 'value': x} if isinstance(x, str) else x
                for x in self.choices
            ]

            answer = self._run_prompt()
            if self.index:
                output = []
                for i, v in enumerate(choice_list):
                    if v in answer:
                        output.append(i)
                return output
            else:
                return answer

        elif choices_type == dict:
            # Check if the input is in the normal form of how pyinquirer takes choices:
            # choices = [{'name': 'stuff'}, {'name': 'things','checked':True}]
            # https://github.com/kazhala/InquirerPy/blob/master/examples/checkbox.py
            normal = True
            for i in self.choices:
                if 'name' not in i or 'value' not in i:
                    normal = False
                    break

            if normal:
                if self.no_input:
                    if self.checked:
                        return [i['name'] for i in self.choices]
                    return []

                if self.index:
                    # TODO: Fix this - low priority
                    raise Exception("Can't index checkbox calls in normal form.")
                return self._run_prompt()

            # Otherwise we expect to reindex the key as the output per this:
            # choices = ['How much stuff?': 'stuff', 'How many things?': 'things']
            choices = []
            if self.no_input:
                if self.checked:
                    for i in self.choices:
                        choices.append(list(i.values())[0])
                    return choices
                return []

            for i in self.choices:
                choices.append(list(i.keys())[0])

            # Fixing to the expected input choices {'name': 'stuff', 'name': ...}
            choices_map = self.choices.copy()
            self.choices = [
                {'name': x, 'value': x} if isinstance(x, str) else x for x in choices
            ]

            answer = self._run_prompt()

            # This is for reindexing the output
            output = []
            for i, v in enumerate(choices_map):
                val = list(v.keys())[0]
                if val in answer:
                    if self.index:
                        output.append(i)
                    else:
                        output.append(v[val])
            return output

    def _run_prompt(self):
        if self.checked:
            choices = [
                Choice(**i, enabled=True) if isinstance(i, dict) else i
                for i in self.choices
            ]
        else:
            choices = self.choices

        question = {
            'type': 'checkbox' if not self.fuzzy else 'fuzzy',
            'name': 'tmp',
            'message': self.message,
            'choices': choices,
        }
        try:
            response = prompt([question])
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)
        return response['tmp']
