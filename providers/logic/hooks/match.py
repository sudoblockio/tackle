import re
from typing import Any, Optional, Union

from tackle import BaseHook, Context, Field, exceptions
from tackle.models import HookCallInput
from tackle.parser import walk_document
from tackle.render import render_string


class MatchHook(BaseHook):
    """
    Hook for match / case statements. Takes a dict where the keys are matched to a
     value. If the case value has an arrow in it (ie key->: ... ) the arrow is stripped
     away. All matched values are ran as hooks.
    """

    hook_name = 'match'
    value: str | int | float | bool = Field(
        True,
        render_by_default=True,
        description="The value to match against. Defaults to boolean true so that "
        "cases can be conditionals.",
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

    def run_key(self, context: Context, value: Any):
        tmp_context = Context(
            # overrides=context.data.overrides,
            verbose=context.verbose,
            no_input=context.no_input,
            key_path=context.key_path.copy(),
            key_path_block=context.key_path.copy(),
            path=context.path,
            data=context.data,
            hooks=context.hooks,
        )

        walk_document(context=tmp_context, value=value.copy())

        return tmp_context.data.public

    def block_macro(
        self,
        context: Context,
        hook_call: HookCallInput,
        key: str,
        val: dict,
    ) -> dict:
        """Take matched input dict and create a `block` hook to parse."""
        # Remove the merge which will be inserted into the parsed block hook.
        merge = hook_call.merge if 'merge' not in val else val['merge']
        if merge:
            # Do this because arrows can stack up and mess up merge
            context.key_path = context.key_path[:-1]
            # We now don't want the hook to be merged
            hook_call.merge = False

        block_hook_input = HookCallInput(**val)
        # TODO: This is likely where the reference is lost for hook_call. Before we
        #  stored the reference in the hook which carried it over to the
        #  hook.skip_output logic in the parser but now we have a new hook so this the
        #  the original reference is lost since we are in a new hook_call reference.
        #  This is an edge case but super useful. Tracking at
        #  https://github.com/sudoblockio/tackle/issues/184

        output = {
            key[-2:]: 'block',
            'merge': merge,
            'items': block_hook_input.model_extra,
        }
        output.update(block_hook_input.__dict__)

        return output

    def match_case(self, context: Context, v: Any):
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
            return self.run_key(context=context, value=v)
        elif isinstance(v, (str, int)):
            self.skip_output = False
            return render_string(context, v)
        self.skip_output = False
        return v

    def match_case_block(
        self,
        context: Context,
        hook_call: HookCallInput,
        k: str,
        v: Any,
    ):
        # Return the value indexed without arrow
        if isinstance(v, str):
            return self.run_key(
                context=context,
                value={k[:-2]: {k[-2:]: v + ' --merge'}},
            )
        elif isinstance(v, dict):
            # We are in a block
            return self.run_key(
                context=context,
                value=self.block_macro(
                    context=context, hook_call=hook_call, key=k, val=v
                ),
            )
        else:
            raise exceptions.HookCallException(
                f"Matched value must be of type string or dict, not {v}.",
                context=context,
            ) from None

    def exec(
        self,
        context: Context,
        hook_call: HookCallInput,
    ) -> Optional[Union[dict, list]]:
        if hook_call is None:
            # This only happens when match is called within jinja rendering which
            # doesn't make sense from a usability perspective.
            raise exceptions.HookCallException(
                "Error calling match hook. Can't use within jinja rendering.",
                context=context,
            )
        if self.value is None:
            self.value = True

        default_value = None
        default_key = None
        # Condition catches everything except expanded hook calls and blocks (ie key->)
        for k, v in self.case.items():
            if k in ['_', '_->']:
                default_value = v
                default_key = k
                # Save this value for later in case nothing is matched
                continue
            if isinstance(k, str) and '{{' in k:
                k = render_string(context, k)
            # if not isinstance(k, str):
            #     if k == self.value:
            #         return v
            #     continue
            try:
                _match = re.fullmatch(str(k), str(self.value))
            except re.error as e:
                raise exceptions.HookCallException(
                    f"Error in match hook case '{k}'\n{e}\nMalformed regex. Must "
                    f"with python's `re` module syntax.",
                    context=context,
                ) from None
            if _match:
                return self.match_case(context=context, v=v)

            elif isinstance(k, bool):
                if k == self.value:
                    return self.match_case(context=context, v=v)
                continue

            # TODO: This regex needs to be modified to not match empty hooks
            #  ie - `->`: x - should not match everything
            # Case where we have an arrow in a key - ie `key->: ...`
            elif re.fullmatch(k[:-2], str(self.value)) and k[-2:] in ('->', '_>'):
                return self.match_case_block(
                    context=context,
                    hook_call=hook_call,
                    k=k,
                    v=v,
                )
        if default_key is not None:
            if '->' in default_key or '_>' in default_key:
                return self.match_case_block(
                    context=context,
                    hook_call=hook_call,
                    k=default_key,
                    v=default_value,
                )
            return self.match_case(context=context, v=default_value)

        raise exceptions.HookCallException(
            f"Value `{self.value}` not found in "
            f"{' ,'.join([i for i in list(self.case)])}",
            context=context,
        ) from None
