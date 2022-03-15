import sys
from pprint import pprint
from typing import Any
from tackle import BaseHook, Field


class PrintHook(BaseHook):
    """
    Hook for printing an input and returning the output.
    [Link](https://docs.python.org/3/library/functions.html#print)
    """

    hook_type: str = 'print'

    objects: Any = Field(None, description="The objects to print.")
    sep: str = Field(' ', description="Separator between printed objects.")
    end: str = Field('\n', description="What to print at the end")
    flush: bool = Field(False, description="No clue.")

    _args: list = ['objects']

    def execute(self) -> None:
        print(self.objects, sep=self.sep, end=self.end, flush=self.flush)


class PprintHook(BaseHook):
    """
    Wraps python pprint builtin.
    [Link](https://docs.python.org/3/library/pprint.html#pprint.PrettyPrinter)
    """

    hook_type: str = 'pprint'

    # fmt: off
    objects: Any = Field(None, description="The object to be pretty printed.")
    indent: int = Field(
        1,
        description="Specifies the amount of indentation added for each nesting level.")
    width: int = Field(
        80,
        description="Specifies the desired maximum number of characters per line in "
                    "the output. If a structure cannot be formatted within the width "
                    "constraint, a best effort will be made.")
    depth: int = Field(
        None,
        description="Controls the number of nesting levels which may be printed; if "
                    "the data structure being printed is too deep, the next contained "
                    "level is replaced by .... By default, there is no constraint on "
                    "the depth of the objects being formatted.")
    compact: bool = Field(
        False,
        description="Impacts the way that long sequences (lists, tuples, sets, etc) "
                    "are formatted. If compact is false (the default) then each item "
                    "of a sequence will be formatted on a separate line. If compact "
                    "is true, as many items as will fit within the width will be "
                    "formatted on each output line.")
    sort_dicts: bool = Field(
        True,
        description="If sort_dicts is true (the default), dictionaries will be "
                    "formatted with their keys sorted, otherwise they will display in "
                    "insertion order.")
    underscore_numbers: bool = Field(
        False,
        description="If underscore_numbers is true, integers will be formatted with "
                    "the _ character for a thousands separator, otherwise underscores "
                    "are not displayed (the default).")
    # fmt: on

    _args: list = ['objects']

    def execute(self) -> None:
        try:
            if sys.version_info.minor < 8:
                pprint(
                    self.objects,
                    indent=self.indent,
                    width=self.width,
                    compact=self.compact,
                )
            elif sys.version_info.minor < 10:
                pprint(
                    self.objects,
                    indent=self.indent,
                    width=self.width,
                    compact=self.compact,
                    sort_dicts=self.sort_dicts,
                )
            elif sys.version_info.minor >= 10:
                pprint(
                    self.objects,
                    indent=self.indent,
                    width=self.width,
                    compact=self.compact,
                    sort_dicts=self.sort_dicts,
                    underscore_numbers=self.underscore_numbers,
                )
        except TypeError as e:
            # TODO: Raise better exception?
            raise e
        return
