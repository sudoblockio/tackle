from typing import Annotated
from pydantic import Field

from tackle import hook, Context, BaseHook


@hook()
def no_inputs():
    return "bar"


@hook()
def required_input(foo: str):
    return foo


@hook()
def non_required_input(foo: str = "bar"):
    return foo


@hook(is_public=True)
def public_hook():
    return "bar"


@hook(is_public=True)
def takes_context(context: Context):
    """A function I can call within a yaml document which has context injected."""
    return context.path.calling.calling_directory


# # Old representation - not tested...
# class UnusedClassName(BaseHook):
#     hook_name = "takes_context_and_var"
#
#     is_public: bool = True
#     # help: str = "A function I can call within a yaml document which has context injected."
#
#     foo: str = Field(description="foo here")
#     args: list = ['foo']
#     def exec(self, context: Context):
#         return context.path.calling.calling_directory


@hook(is_public=True)
def takes_context_and_var(
    context: Context, foo: Annotated[str, Field(description="foos")]):
    return context.path.calling.calling_directory


@hook(is_public=True)
def annotated_field(foo: Annotated[int, Field(lt=1)]):
    return foo


# @hook(is_public=True)
# def some_args(*a: str):
#     # TODO: Doesn't work - need to make args not typed... - hook_args...
#     return a
#
#
# @hook(is_public=True)
# def some_kwargs(**kwargs):
#     # TODO: Doesn't error but needs same fix as above
#     return kwargs
