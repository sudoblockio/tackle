# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import sys
import logging
import subprocess
import errno
import os
import pty
from select import select

import click


from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class CommandOperator(BaseOperator):
    """
    `command` operator for system calls.

    Hides streaming output. To view streaming output of command use the `shell`
    operator.

    :param command: The command to run on the host
    :return String output of command
    """

    type = 'command'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize `command` Hook."""  # noqa
        super(CommandOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """Run the operator."""
        p = subprocess.Popen(
            self.operator_dict['command'],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, err = p.communicate()

        if err:
            sys.exit(err)

        return output.decode("utf-8")


class ShellOperator(BaseOperator):
    """
    `Shell` operator for system calls.

    Streams the output of the process.

    :param command: The command to run on the host
    :return String output of command
    """

    type = 'shell'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize `command` Hook."""  # noqa
        super(ShellOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """Run the operator."""
        masters, slaves = zip(pty.openpty(), pty.openpty())
        cmd = self.operator_dict['command'].split()

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
                                click.echo(data.rstrip())
                            else:  # We caught stderr
                                click.echo(data.rstrip(), err=True)
                            readable[fd].flush()
        for fd in masters:
            os.close(fd)
        logger.debug("Process exited with %s return code." % p.returncode)
        return data.decode("utf-8")
