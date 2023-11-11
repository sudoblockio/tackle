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


__all__ = [
    'tackle',
    'Field',
    'BaseHook',
    'HookCallInput',
    'Context',
    'settings',
    'DocumentKeyType',
    'DocumentType',
    'DocumentValueType',
]
