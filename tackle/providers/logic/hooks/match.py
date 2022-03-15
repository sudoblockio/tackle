"""Match hook."""
from typing import Union
import re

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

    _render_exclude = {'case'}
    _args = ['value']
    _docs_order = 3

    def execute(self) -> Union[dict, list]:
        # Condition catches everything except expanded hook calls and blocks (ie key->)
        for k, v in self.case.items():
            if re.match(k, self.value):
                # Dicts that are not expanded hooks themselves
                if isinstance(v, dict) and not ('->' in v or '_>' in v):
                    return self.run_key(v)
                return self.run_key(k, v)[k]

            elif re.match(k[:-2], self.value) and k[-2:] in ('->', '_>'):
                # Return the value indexed without arrow
                return self.run_key(k, v)[k[:-2]]

        raise Exception(f"Value `{self.value}` not found in {self.case.keys()}")

    def run_key(self, key, value=None):
        if value:
            case_value = {key: value}
        else:
            case_value = key

        # Bring in the current input dict
        existing_context = self.output_dict.copy()
        existing_context.update(self.existing_context)

        # Create a temporary context
        tmp_context = Context(
            provider_hooks=self.provider_hooks,
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
