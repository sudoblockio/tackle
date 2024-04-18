from typing import Any

from tackle import BaseHook, Field


class PythonTypesHook(BaseHook):
    hook_name = 'python_types'
    help: str = "A python hook"
    a_str: str = 'foo'
    a_str_required: str = Field(..., description="str_desc")
    an_optional_str: str | None = None
    any_str: Any = None

    is_public: bool = True
