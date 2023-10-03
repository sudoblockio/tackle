from typing import Union

from tackle import Context, BaseHook, Field
from tackle.parser import walk_document
from tackle.render import render_string
from tackle.exceptions import HookCallException
from tackle.utils.render import wrap_braces_if_not_exist


class MatchHook(BaseHook):
    """
    Hook for while loops. Takes a condition and runs a context in a loop until the
    condition is met.

    Not Implemented yet.
    """

    hook_name: str = 'while'
    condition: str = Field(
        ..., description="A jinja expression to evaluated on each pass through `run`."
    )
    do: Union[dict, list] = Field(
        ...,
        description="A list or dictionary to parse same as tackle file.",
    )

    args: list = ['condition']

    def do_walk(self) -> Context:
        # TODO:
        public_context = {}

        tmp_context = Context(
            input_context=self.do,
            key_path=self.key_path.copy(),
            key_path_block=self.key_path.copy(),
            # provider_hooks=self.provider_hooks,
            public_hooks=self.public_hooks,
            private_hooks=self.private_hooks,
            public_context=public_context,
            private_context=self.private_context,
            temporary_context=self.public_context,
            existing_context=self.existing_context,
            no_input=self.no_input,
            calling_directory=self.calling_directory,
            calling_file=self.calling_file,
            verbose=self.verbose,
            override_context=self.override_context,
        )
        walk_document(context=tmp_context, value=self.do.copy())
        return tmp_context

    def do_while(self):
        output = []

        while True:
            tmp_context = self.do_walk()

            rendered_condition = render_string(
                tmp_context,
                wrap_braces_if_not_exist(self.condition),
            )

            if not isinstance(rendered_condition, bool):
                raise HookCallException(
                    f"Condition `{self.condition}` needs to render to boolean. "
                    f"Currently renders as {rendered_condition}.",
                    context=self,
                ) from None

            output.append(tmp_context.public_context)
            # tmp_context.existing_context = tmp_context.public_context
            # tmp_context.public_context = {}

            if rendered_condition:
                break

        return output


    def exec(self) -> list:
        if isinstance(self.do, dict):
            return self.do_while()
        elif isinstance(self.do, list):
            pass
        elif isinstance(self.do, str):
            self.do = {'item': self.do}
            output = self.do_while()

            return [i['item'] for i in output]
        else:
            raise HookCallException
