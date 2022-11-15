import re

from tackle.models import BaseHook, Field


class StartsWithHook(BaseHook):
    """
    Hook checking if a string starts with another string.
    [Docs](https://www.tutorialspoint.com/python/string_startswith.htm)
    """

    hook_type: str = 'starts_with'

    input: str = Field(..., description="A string to check")
    match: str = Field(..., description="The chars to match")

    beg: int = Field(
        None,
        description="This is the optional parameter to set start "
        "index of the matching boundary.",
    )
    end: int = Field(
        None,
        description="This is the optional parameter to end start "
        "index of the matching boundary.",
    )

    args: list = ['input', 'match']
    _docs_order = 8

    def exec(self):
        return self.input.startswith(self.match)


class EndsWithHook(BaseHook):
    """
    Hook checking if a string ends with another string.
    [Docs](https://www.tutorialspoint.com/python/string_startswith.htm)
    """

    hook_type: str = 'ends_with'

    input: str = Field(..., description="A string to check")
    match: str = Field(..., description="The chars to match")

    beg: int = Field(
        None,
        description="This is the optional parameter to set start "
        "index of the matching boundary.",
    )
    end: int = Field(
        None,
        description="This is the optional parameter to end start "
        "index of the matching boundary.",
    )

    args: list = ['input', 'match']
    _docs_order = 8

    def exec(self):
        return self.input.endswith(self.match)


class RegexMatchHook(BaseHook):
    """
    Hook running a regex against a string.
    [Docs](https://docs.python.org/3/library/re.html#re.match)
    """

    hook_type: str = 'regex_match'

    pattern: str = Field(..., description="A regex pattern to check.")
    string: str = Field(..., description="A string to check.")

    args: list = ['pattern', 'string']

    def exec(self):
        return re.match(self.pattern, self.string)
