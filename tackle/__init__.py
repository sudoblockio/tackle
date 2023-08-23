"""Main package for tackle."""
__version__ = "0.5.1"  # x-release-please-version

from tackle.settings import settings
from tackle.models import (
    Context,
    BaseHook,
)
from tackle.pydantic.fields import Field
from tackle.types import (
    DocumentKeyType,
    DocumentType,
    DocumentValueType,
    # HookType,
)

import sys

if 'pytest' in sys.modules:
    from tackle.main import tackle
else:
    from tackle.main import tackle

__all__ = [
    'tackle',
    'Field',
    'BaseHook',
    'Context',
    'settings',
    'DocumentKeyType',
    'DocumentType',
    'DocumentValueType',
    'HookType',
]
