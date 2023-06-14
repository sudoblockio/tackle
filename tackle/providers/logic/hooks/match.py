"""Match hook."""
from typing import Union, Optional, Any
import re

from tackle.models import BaseHook, Context, Field
from tackle.parser import walk_element
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

    skip_output: bool = True
    _render_exclude = {'case'}
    _docs_order = 3

    def run_key(self, value):
        if self.temporary_context is None:
            self.temporary_context = {}

        tmp_context = Context(
            input_context=value,
            key_path=self.key_path.copy(),
            key_path_block=self.key_path.copy(),
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
            override_context=self.override_context,
        )
        walk_element(context=tmp_context, element=value.copy())

        return tmp_context.public_context

    def block_macro(self, key: str, val: dict) -> dict:
        """Take matched input dict and create a `block` hook to parse."""
        # Remove the merge which will be inserted into the parsed block hook.
        merge = self.merge if 'merge' not in val else val['merge']
        if merge:
            # Do this because arrows can stack up and mess up merge
            self.key_path = self.key_path[:-1]
            # We now don't want the hook to be merged
            self.merge = False

        output = {
            key[-2:]: 'block',
            'merge': merge,
            'items': {},
        }
        # Have a collection of fields that are part of the base.
        aliases = [v.alias for _, v in BaseHook.__fields__.items()] + ['->', '_>']
        for k, v in val.items():
            if k not in aliases:
                # Set the keys under the `items` key per the block hook's input
                output['items'].update({k: v})
            else:
                output.update({k: v})
        return output

    def match_case(self, v: Any):
        # Normal dicts
        if isinstance(v, dict) and not ('->' in v or '_>' in v):
            # TODO: Determine if `match` hook should parse dictionaries by default
            #  https://github.com/sudoblockio/tackle/issues/160
            #  This will change to something like this but k will have a `->` suffixed:
            # return self.run_key(self.block_macro(k, v))
            self.skip_output = False
            return v
        # Dicts that are expanded hooks
        elif isinstance(v, dict):
            return self.run_key(v)
        elif isinstance(v, (str, int)):
            self.skip_output = False
            return render_string(self, v)
        self.skip_output = False
        return v

    def match_case_block(self, k: str, v: Any):
        # Return the value indexed without arrow
        if isinstance(v, str):
            return self.run_key({k[:-2]: {k[-2:]: v + ' --merge'}})
        elif isinstance(v, dict):
            # We are in a block
            return self.run_key(self.block_macro(k, v))
        else:
            raise HookCallException(
                f"Matched value must be of type string or dict, not {v}.",
                context=self,
            ) from None

    def exec(self) -> Optional[Union[dict, list]]:
        default_value = None
        default_key = None
        # Condition catches everything except expanded hook calls and blocks (ie key->)
        for k, v in self.case.items():
            if k in ['_', '_->']:
                default_value = v
                default_key = k
                # Save this value for later in case nothing is matched
                continue
            try:
                _match = re.fullmatch(k, self.value)
            except re.error as e:
                raise HookCallException(
                    f"Error in match hook case '{k}'\n{e}\nMalformed regex. Must "
                    f"with python's `re` module syntax.",
                    context=self,
                ) from None
            if _match:
                return self.match_case(v=v)

            # TODO: This regex needs to be modified to not match empty hooks
            #  ie - `->`: x - should not match everything
            # Case where we have an arrow in a key - ie `key->: ...`
            elif re.fullmatch(k[:-2], self.value) and k[-2:] in ('->', '_>'):
                return self.match_case_block(k, v)
        if default_key is not None:
            if '->' in default_key or '_>' in default_key:
                return self.match_case_block(k=default_key, v=default_value)
            return self.match_case(v=default_value)

        raise HookCallException(
            f"Value `{self.value}` not found in "
            f"{' ,'.join([i for i in list(self.case)])}",
            context=self,
        ) from None
