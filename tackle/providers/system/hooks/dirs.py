# """Path hooks."""
import logging
import pathlib

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class MakeDirectoryHook(BaseHook):
    """Hook creating a directory.

    :param path: The path to file or directory
    :return: boolean:
    """

    type: str = 'mkdir'
    path: str

    _args: list = ['path']

    def execute(self):
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        return self.path
