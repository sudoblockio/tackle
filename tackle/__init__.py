"""Main package for tackle."""
__version__ = "0.7.2"  # x-release-please-version

from pydantic import Field

from tackle.context import Context
from tackle.decorators import public, private, hook
from tackle.factory import new_context
from tackle.main import tackle
from tackle.models import BaseHook, HookCallInput
from tackle.settings import settings
from tackle.types import DocumentKeyType, DocumentType, DocumentValueType
from tackle.utils.hooks import get_hook

__all__ = [
    'tackle',
    'hook',
    'BaseHook',
    'public',
    'private',
    'Field',
    'HookCallInput',
    'Context',
    'settings',
    'get_hook',
    'new_context',
    'DocumentKeyType',
    'DocumentType',
    'DocumentValueType',
]
