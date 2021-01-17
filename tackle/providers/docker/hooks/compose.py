# -*- coding: utf-8 -*-

"""Docker compose hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import re
import os
import subprocess
from pydantic import validator

from tackle.exceptions import HookCallException
from tackle.utils.context_manager import work_in
from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class DockerComposeHook(BaseHook):
    """Hook for running docker compose commands.

    :return:
    """

    type: str = 'docker_compose'

    command: str = None
    files: list = None
    env_file: str = None
    output_file: str = None
    run: bool = True

    verbose: bool = False
    log_level: str = None

    file_name_prefix: str = "docker-compose"

    @validator('log_level')
    def passwords_match(cls, v, values, **kwargs):
        if 'log_level' in values and v not in [
            'DEBUG',
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL',
        ]:
            raise HookCallException(
                'In docker_compose hook, log_level should '
                'be one of DEBUG, INFO, WARNING, ERROR, CRITICAL'
            )
        return v

    def fix_docker_compose_file_name(self, file):
        """Fix abbreviated files names."""
        if os.path.isfile(file):
            return file

        for f in os.listdir():
            regex = f"^{self.file_name_prefix}.{file}.(yml|yaml)"
            match = re.compile(regex).match(f)
            if match:
                return match.string
        print(
            f"Could not find file='{file}' in docker_compose "
            f"operator for key='{self.key}'."
        )

    def get_file_names(self, cmd):
        """Get the file names from list."""
        for f in self.files:
            # Case where there is a directory
            if os.path.isdir(os.path.dirname(f)):
                with work_in(os.path.dirname(f)):
                    filename = self.fix_docker_compose_file_name(f.split('/')[-1])
                    if not filename:
                        continue
                    path = os.path.join(os.path.dirname(f), filename)
                    cmd += [f"-f {path}"]
            # Normal case where docker-compose file is in the current working directory.
            else:
                filename = self.fix_docker_compose_file_name(f)
                if not filename:
                    continue
                cmd += [f"-f {filename}"]

    def execute(self):
        """Wrap the docker-compose command."""
        cmd = ["docker-compose"]
        if self.files:
            self.get_file_names(cmd)

        #  Env file
        if self.env_file:
            cmd.append(f"--env-file {self.env_file}")
        # Log level
        if self.log_level:
            cmd.append(f"--log-level {self.log_level}")
        # Verbose
        if self.log_level:
            cmd.append(f"--log-level {self.log_level}")

        #  Append the command
        cmd.append(self.command)

        # Append to output file
        if self.output_file:
            cmd.append(f"> {self.output_file}")

        # Run the output
        command_str = ' '.join(cmd)
        if self.run:
            p = subprocess.Popen(
                command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, err = p.communicate()

            if err:
                raise HookCallException(err)

        return command_str
