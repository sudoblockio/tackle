# from tackle import BaseHook, Field
#
#
# class MapListKeyValuesHook(BaseHook):
#     """
#     Hook for creating a list of maps from a map with keys as `key` + `value` from the
#      map. Useful for some operations that require maps as lists with these keys.
#     """
#
#     hook_type: str = 'map_to_list_key_values'
#     # fmt: off
#     src: dict = Field(
#         ..., description="A map to extract the keys out of.", render_by_default=True)
#     # fmt: on
#
#     args: list = ['src']
#
#     def exec(self) -> list:
#         output = []
#         for k, v in self.src.items():
#             output.append({'key': k, 'value': v})
#
#         return output
