import logging
import pathlib

from tackle.models import BaseHook, Field

logger = logging.getLogger(__name__)


class MakeDirectoryHook(BaseHook):
    """Hook creating a directory."""

    hook_type: str = 'mkdir'
    path: str = Field(..., description="The path to file or directory")

    _args: list = ['path']
    _docs_order = 1

    def execute(self) -> str:
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        return self.path
