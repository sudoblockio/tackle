"""Match hook."""
from typing import Union

from tackle.models import BaseHook, Context, Field
from tackle.parser import walk_sync


class MatchHook(BaseHook):
    """
    Hook for match / case statements. Takes a dict where the keys are matched to a
    value. If the case value has an arrow in it (ie key->: ... ) the arrow is stripped
    away. All matched values are ran as hooks.
    """

    hook_type: str = 'match'
    value: str = Field(
        ..., render_by_default=True, description="The value to match against."
    )
    case: dict = Field(
        ...,
        description="A dictionary where the keys are cases to be matched. Runs hooks "
        "if present.",
    )

    _args = ['value']
    _docs_order = 3

    def execute(self) -> Union[dict, list]:
        # Condition catches everything except expanded hook calls and blocks (ie key->)
        if self.value in self.case:
            return self.run_key()[self.value]
        else:
            # Iterate through keys and find keys matching value without arrow (->, _>)
            for k, v in self.case.items():
                if self.value == k[:-2]:
                    # Rewrite the value to match the key
                    self.value = k
                    output_dict = self.run_key()
                    # Return the value indexed without arrow
                    return output_dict[k[:-2]]
            raise Exception(f"Value `{self.value}` not found in {self.case.keys()}")

    def run_key(self):
        case_value = {self.value: self.case[self.value]}

        # TODO: Make the context dependent on type.
        #  https://github.com/robcxyz/tackle-box/issues/26
        # If the matched case is a string - Run that -- Will need change to above
        # If it is a dict / list - Parse that directly without indenting with the case
        # if isinstance(self.case[self.value], (str, int, float)):
        #     pass

        # Bring in the current input dict
        existing_context = self.output_dict.copy()
        existing_context.update(self.existing_context)

        # Create a temporary context
        tmp_context = Context(
            providers=self.providers,
            existing_context=existing_context,
            output_dict={},
            input_dict=case_value,
            key_path=[],
            no_input=self.no_input,
            calling_directory=self.calling_directory,
        )
        # Traverse the input and update the output dict
        walk_sync(tmp_context, element=case_value.copy())
        # Reindex the return based on self.value
        return tmp_context.output_dict
