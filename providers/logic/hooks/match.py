from typing import Union, Optional, Any
import re

from tackle import BaseHook, Context, Field
from tackle.models import HookCallInput
from tackle.parser import walk_document
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
        ...,
        render_by_default=True,
        description="The value to match against."
    )
    case: dict = Field(
        ...,
        description="A dictionary where the keys are cases to be matched. Runs hooks "
                    "if present.",
    )

    args: list = ['value']

    skip_output: bool = True
    render_exclude: list = ['case']
    _docs_order = 3

    def run_key(self, value):

        tmp_context = Context(
            # overrides=self.context.data.overrides,
            verbose=self.context.verbose,
            no_input=self.context.no_input,
            key_path=self.context.key_path.copy(),
            key_path_block=self.context.key_path.copy(),
            path=self.context.path,
            data=self.context.data,
            hooks=self.context.hooks,
        )

        walk_document(context=tmp_context, value=value.copy())

        return tmp_context.data.public

    def block_macro(self, key: str, val: dict) -> dict:
        """Take matched input dict and create a `block` hook to parse."""
        # Remove the merge which will be inserted into the parsed block hook.
        merge = self.hook_call.merge if 'merge' not in val else val['merge']
        if merge:
            # Do this because arrows can stack up and mess up merge
            self.context.key_path = self.context.key_path[:-1]
            # We now don't want the hook to be merged
            self.hook_call.merge = False

        block_hook_input = HookCallInput(**val)

        output = {
            key[-2:]: 'block',
            'merge': merge,
            'items': block_hook_input.model_extra,
        }
        output.update(block_hook_input.__dict__)

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
            return render_string(self.context, v)
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
                context=self.context,
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
                    context=self.context,
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
            context=self.context,
        ) from None
