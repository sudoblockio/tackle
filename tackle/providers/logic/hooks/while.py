# from typing import Union
#
# from tackle.models import BaseHook, Field
#
#
# class MatchHook(BaseHook):
#     """
#     Hook for while loops. Takes a condition and runs a context in a loop until the
#     condition is met.
#
#     Not Implemented yet.
#     """
#
#     hook_type: str = 'while'
#     condition: str = Field(
#         ..., description="A jinja expression to evaluated on each pass through `run`."
#     )
#     run: Union[dict, list] = Field(
#         ...,
#         description="A list or dictionary to parse same as tackle file.",
#     )
#
#     args: list = ['condition']
#
#     def exec(self) -> Union[dict, list]:
#         raise NotImplementedError
