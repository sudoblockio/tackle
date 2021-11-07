"""Main package for tackle box."""
__version__ = "0.1.1-alpha.1"

from pydantic import Field
from tackle.models import BaseHook

from tackle.main import tackle

__all__ = [
    'tackle',
]
