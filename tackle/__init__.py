"""Main package for tackle."""
__version__ = "0.5.1"  # x-release-please-version

from pydantic import Field

from tackle.settings import settings
from tackle.models import (
    BaseHook,
    HookCallInput,
)
from tackle.context import Context
from tackle.main import tackle
from tackle.types import (
    DocumentKeyType,
    DocumentType,
    DocumentValueType,
)
from tackle.utils.hooks import get_hook
from tackle.factory import new_context


__all__ = [
    'tackle',
    'Field',
    'BaseHook',
    'HookCallInput',
    'Context',
    'settings',
    'get_hook',
    'new_context',
    'DocumentKeyType',
    'DocumentType',
    'DocumentValueType',
]
