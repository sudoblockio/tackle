"""Main package for tackle box."""
__version__ = "0.2.1-alpha.1"

from tackle.models import BaseHook
from tackle.models import Field

from tackle.main import tackle

__all__ = [
    'tackle',
]
