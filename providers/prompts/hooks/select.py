import sys
from typing import Any, List, Union

from InquirerPy import prompt

from tackle import BaseHook, Context, Field, exceptions
from tackle.utils.data_crud import get_readable_key_path


class InquirerListHook(BaseHook):
    """
    Hook for PyInquirer 'list' type prompts, a single selector that returns a string.
     Takes in two forms of `choices` inputs, list of string or list of maps with the
     key as the question and the value as the output.
     [Source example](https://github.com/kazhala/InquirerPy/blob/master/examples/list.py)
    """

    hook_name = 'select'

    message: str = Field(
        None,
        description="String message to show when prompting.",
    )
    choices: Union[List[str], List[dict]] = Field(
        ...,
        description="List of strings or dicts with keys as output and values as display.",
        render_by_default=True,
    )
    index: bool = Field(
        False, description="Boolean to return the index instead of the answer"
    )

    args: list = ['message']
    _docs_order = 1

    def exec(self, context: Context) -> Any:
        if self.message is None:
            self.message = get_readable_key_path(context.key_path) + ' >>>'

        # Figure out what type of dictionary it is
        choices_type = None
        for i, v in enumerate(self.choices):
            if i != 0 and type(v) != choices_type:  # noqa: E721
                raise ValueError("All items need to be of the same type in ")
            choices_type = type(v)

        if choices_type == str:
            answer = self._run_prompt(context=context)
            if self.index:
                return self.choices.index(answer)
            else:
                return answer
        elif choices_type == dict:
            choice_list = self.choices.copy()
            self.choices = []
            for i in choice_list:
                self.choices.append(list(i.keys())[0])

            answer = self._run_prompt(context=context)
            for i, v in enumerate(choice_list):
                if answer == list(v.keys())[0]:
                    if self.index:
                        return i
                    else:
                        return list(v.values())[0]
        else:
            raise ValueError(
                "Choices must be list of string or dict with displayed "
                "choices as keys and output selection as the value."
            )

    def _run_prompt(self, context: Context):
        if not context.no_input:
            question = {
                'type': 'list',
                'name': 'tmp',
                'message': self.message,
                'choices': self.choices,
            }

            # Handle keyboard exit
            try:
                response = prompt([question])
            except KeyboardInterrupt:
                print("Exiting...")
                sys.exit(0)
            except EOFError:
                raise exceptions.PromptHookCallException(context=context)
            return response['tmp']

        elif isinstance(self.choices[0], str):
            return self.choices[0]
        elif isinstance(self.choices[0], dict):
            return list(self.choices[0].keys())[0]
