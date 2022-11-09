from operator import itemgetter
from typing import Union, Optional

from tackle import BaseHook, Field
from tackle.utils.dicts import encode_key_path, nested_get
from tackle.exceptions import HookCallException


class SortHook(BaseHook):
    """
    Hook for sorting complex lists, dicts, or items within a key both in place or as
     output.
    """

    hook_type: str = 'sort'
    # fmt: off
    src: Union[list, dict, str] = Field(
        ...,
        description="Either a list of strings or a dict with keys to sort and return "
                    "the output or a string key_path to sort both in place or as "
                    "output (see `in_place`).")
    key: str = Field(
        None,
        description="If the `src` is a list of maps, the key to sort the contents by."
    )
    in_place: bool = Field(
        True, description="If the `src` is a string (ie a key path), then sort the "
                          "item in place (ie replace original) and return None.")
    reverse: bool = Field(False, description="To sort in reverse.")

    # TODO: Allow sorting the context based on key path
    # key: str = Field(...)
    src_is_key_path: bool = Field(
        False, description="If the src is a list and is meant to be a key path.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    index: Union[int, list] = Field(
        None,
        description="If the input `src` is a list, use the index as the sort key. "
        "Takes both an int for single index or list for multiple criteria.",
    )
    args: list = ['src']

    def sort(self, src):
        if isinstance(src, list):
            if all(isinstance(n, dict) for n in src):
                # Iterrand is a dict
                return sorted(src, key=lambda d: d[self.key])

            if self.index is None:
                return src.sort(reverse=self.reverse)
            else:
                # TODO: Untested
                if isinstance(self.index, int):
                    # Source: https://stackoverflow.com/a/15544861/12642712
                    sorted_list = sorted(
                        src,
                        key=itemgetter(self.index),
                        reverse=self.reverse,
                    )
                    return sorted_list
                else:
                    # TODO: Untested
                    # TODO: wtf?
                    sorted_list = sorted(
                        src,
                        key=itemgetter(*self.index),
                        reverse=self.reverse,
                    )
                    return sorted_list
        else:
            # TODO: Untested
            # https://stackoverflow.com/a/613218/12642712
            sorted_dict = {
                k: v
                for k, v in sorted(
                    src.items(),
                    key=lambda item: item[1],
                    reverse=self.reverse,
                )
            }
            return sorted_dict

    def get_src(self):
        value = None
        contexts = ['public', 'private', 'temporary', 'existing']
        for i in contexts:
            try:
                value = nested_get(
                    element=getattr(self, f'{i}_context'),
                    keys=encode_key_path(self.src, self.sep),
                )
            except KeyError:
                pass

            if value is not None:
                break

        if value is None:
            raise HookCallException(
                f"Could not find {self.src} in any of the contexts (ie in "
                f"{','.join(contexts)}).",
                hook=self,
            )
        return value

    def exec(self) -> Optional[Union[list, dict]]:
        if (
            isinstance(self.src, str)
            or self.src_is_key_path
            and isinstance(self.src, list)
        ):
            self.src_is_key_path = True

            if self.in_place:
                self.src = self.get_src()
                return self.sort(self.src)
                # return self.src
            else:
                src = self.get_src()
                self.sort(src)
                return src
        else:
            # TODO: Untested
            self.sort(self.src)
            return self.src
