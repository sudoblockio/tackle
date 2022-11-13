from tackle import BaseHook, Field
from tackle.parser import get_hook


class FlattenHook(BaseHook):
    """
    Hook for flattening args/kwargs/flags into CLI inputs. Takes a declarative hook
    input and turns it into a string that can be used to call a generic CLI program.
    """

    hook_type: str = 'flatten'
    hook: str = Field(None, description="A hook")

    positional_args: list = Field(
        None, description="A list of args that should be considered positional."
    )
    inputs: dict = Field(
        None, description="A dictionary of arguments to use when flattening."
    )
    kwargs: str = 'inputs'
    args: list = ['hook', 'positional_args']

    def exec(self) -> str:
        if self.inputs is None:
            self.inputs: dict = self.existing_context

        hook = get_hook(context=self, hook_type=self.hook)
        if hook is None:
            raise Exception(f"The hook={self.hook} was not found.")

        flat_items = []
        for i in hook.__fields__['args'].default:
            hook_value = self.inputs[i]
            # TODO: Implment a skip or something?
            # hook.__fields__[i].default
            flat_items.append(hook_value)

        for i in hook.__fields__['function_fields'].default:
            hook_field = hook.__fields__[i]
            hook_value = self.inputs[i]

            if hook_field.type_ == bool:
                if hook_field.name in self.inputs and self.inputs[hook_field.name]:
                    flat_items.append("--" + hook_field.name)
                elif hook_field.default:
                    flat_items.append("--" + hook_field.name)
            elif hook_field.type_ in (str, int, float):
                if hook_field.name in hook.__fields__['args'].default:
                    continue
                if hook_value == hook.__fields__[hook_field.name].default:
                    continue
                flat_items.append("--" + hook_field.name)
                flat_items.append(hook_value)
            else:
                raise NotImplementedError(
                    "No other meanings to types have been determined"
                )
            pass

        return ' '.join(flat_items)
