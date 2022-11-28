import os

from tackle.models import BaseHook, Field


class OsSystemHook(BaseHook):
    """Run system commands via os.system(command). WIP"""

    hook_type: str = 'os_system'

    command: str = Field(..., description="A shell command.")
    args: list = ['command']

    def exec(self) -> None:
        os.system(self.command)
