import sys
import logging
import subprocess
import errno
import struct
import shutil
import os
from itertools import chain
from select import select
from pydantic import Field
from typing import Any

from tackle.models import BaseHook
from tackle.exceptions import HookCallException

if os.name != 'nt':
    # Don't import on windows as pty is not available there
    import pty
    import fcntl
    import termios

logger = logging.getLogger(__name__)


class CommandFailedException(Exception):
    """Exception to stop crazy stack traces everytime an errored command is run."""

    def __init__(self, message=None):
        sys.tracebacklimit = 0
        self.message = message


class CommandHook(BaseHook):
    """Run system commands."""

    hook_type: str = 'command'

    command: str = Field(..., description="A shell command.")
    ignore_error: bool = Field(False, description="Ignore errors.")
    multiline: bool = Field(False, description="Don't automatically breakup lines")

    system: bool = Field(
        False,
        description="Use python's os.system command instead of popen based stream "
        "reader.",
    )

    args: list = ['command']

    def _set_size(self, fd):
        """Found at: https://stackoverflow.com/a/6420070."""
        (
            _COLUMNS,
            _ROWS,
        ) = shutil.get_terminal_size(fallback=(80, 20))
        size = struct.pack("HHHH", _ROWS, _COLUMNS, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, size)

    def exec(self) -> Any:
        # TODO: Fix multi-line calls
        # https://github.com/robcxyz/tackle/issues/14
        if self.multiline:
            commands = [self.command.replace('\n', ' ').split()]
        else:
            commands = [i.split() for i in self.command.split('\n')]
            if commands[-1] == []:
                commands.pop()

        data = bytes()
        output = []
        for cmd in commands:
            masters, slaves = zip(pty.openpty(), pty.openpty())
            for fd in chain(masters, slaves):
                self._set_size(fd)

            try:
                with subprocess.Popen(
                    cmd, stdin=slaves[0], stdout=slaves[0], stderr=slaves[1]
                ) as p:
                    for fd in slaves:
                        os.close(fd)  # no input
                        readable = {
                            masters[0]: sys.stdout.buffer,  # store buffers seperately
                            masters[1]: sys.stderr.buffer,
                        }
                    while readable:
                        # TODO: Session is not interactive and fails below when interactive
                        #  prompts are displayed
                        # https://github.com/robcxyz/tackle/issues/13
                        # x = select(readable, [], [])[0]
                        for fd in select(readable, [], [])[0]:
                            try:
                                data = os.read(fd, 1024)  # read available
                            except OSError as e:
                                if e.errno != errno.EIO:
                                    raise  # XXX cleanup
                                del readable[fd]  # EIO means EOF on some systems
                            else:
                                if not data:  # EOF
                                    del readable[fd]
                                else:
                                    if fd == masters[0]:  # We caught stdout
                                        # TODO: Interactive prompts
                                        print(data.rstrip().decode('utf-8'))
                                    else:  # We caught stderr
                                        print(data.rstrip().decode('utf-8'))
                                    readable[fd].flush()
                # for fd in masters:
                #     os.close(fd)
                logger.debug("Process exited with %s return code." % p.returncode)
                if p.returncode != 0 and not self.ignore_error:
                    if self.verbose:
                        raise HookCallException(data.decode('utf-8'))
                    else:
                        # Exception already printed
                        raise CommandFailedException()
                else:
                    # return data.decode("utf-8")
                    output.append(data.decode("utf-8"))

            except Exception as e:
                if self.ignore_error:
                    return e
                else:
                    raise e

        for fd in masters:
            os.close(fd)

        return '\n'.join(output)


# class CommandHook(BaseHook):
#     """System commands."""
#
#     hook_type: str = 'command'
#
#     command: str = Field(..., description="A shell command.")
#     ignore_error: bool = Field(False, description="Ignore errors.")
#
#     args: list = ['command']
#
#     def exec(self) -> Any:
#         p = subprocess.Popen(
#             self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
#         )
#         output, err = p.communicate()
#
#         if err and not self.ignore_error:
#             raise HookCallException(err.decode('utf-8'))
#         if err and self.ignore_error:
#             return err.decode('utf-8')
#
#         return output.decode("utf-8")
