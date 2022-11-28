"""Match hook."""
from typing import Union
import re

from tackle.models import BaseHook, Context, Field
from tackle.parser import walk_sync
from tackle.render import render_string
from tackle.exceptions import HookCallException


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

    args: list = ['value']

    _render_exclude = {'case'}
    _docs_order = 3

    def block_macro(self, key, val) -> dict:
        """Take input and create a block hook to parse."""
        output = {key[-2:]: 'block', 'merge': True}
        aliases = [v.alias for _, v in BaseHook.__fields__.items()] + ['->', '_>']
        for k, v in val.items():
            if k not in aliases:
                # Set the keys under the `items` key per the block hook's input
                output.update({'items': {k: v}})
            else:
                output.update({k: v})
        if self.verbose:
            print(
                "You are likely going to hit a bug."
                "https://github.com/robcxyz/tackle/issues/67"
            )
        return {key[:-2]: output}
        # return output

    def exec(self) -> Union[dict, list]:
        # Condition catches everything except expanded hook calls and blocks (ie key->)
        for k, v in self.case.items():
            if re.match(k, self.value):
                # Dicts that are not expanded hooks themselves
                if isinstance(v, (dict, list)) and not ('->' in v or '_>' in v):
                    return self.run_key(v)
                elif isinstance(v, dict):
                    # return self.run_key({k: {**v, **{'merge': True}}})
                    return self.run_key({k: {**v, **{'merge': True}}})
                elif isinstance(v, str):
                    return render_string(self, v)
                return v

            elif re.match(k[:-2], self.value) and k[-2:] in ('->', '_>'):
                # Return the value indexed without arrow
                if isinstance(v, str):
                    return self.run_key({k[:-2]: {k[-2:]: v + ' --merge'}})
                elif isinstance(v, dict):
                    return self.run_key(self.block_macro(k, v))
                else:
                    raise HookCallException(
                        f"Matched value must be of type string or dict, not {v}.",
                        context=self,
                    ) from None

        raise Exception(f"Value `{self.value}` not found in {self.case.keys()}")

    def run_key(self, value):
        self.skip_output: bool = True

        tmp_context = Context(
            input_context=value,
            key_path=self.key_path.copy(),
            key_path_block=self.key_path.copy(),
            # provider_hooks=self.provider_hooks,
            public_hooks=self.public_hooks,
            private_hooks=self.private_hooks,
            public_context=self.public_context,
            private_context=self.private_context,
            temporary_context=self.temporary_context,
            existing_context=self.existing_context,
            no_input=self.no_input,
            calling_directory=self.calling_directory,
            calling_file=self.calling_file,
            verbose=self.verbose,
        )
        walk_sync(context=tmp_context, element=value.copy())

        return self.public_context
