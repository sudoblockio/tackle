"""Special variables to be used in rendering."""

import os
import platform

import distro

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context


def get_vars(context: 'Context'):
    """Get special variables."""
    vars = {
        'cwd': os.getcwd(),
        'home_dir': os.path.expanduser('~'),
        'system': platform.system(),
        'platform': platform.platform(),
        'release': platform.release(),
        'version': platform.version(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'calling_directory': context.calling_directory,
        'key': context.context_key,
        'tackle_gen': context.tackle_gen,
        'this': dict(context.output_dict),
        'output': context.output_dict,
    }
    if platform.system() == 'Linux':
        linux_id_name, linux_version, linux_codename = distro.linux_distribution(
            full_distribution_name=False
        )
        linux_vars = {
            'linux_id_name': linux_id_name,
            'linux_version': linux_version,
            'linux_codename': linux_codename,
        }
        vars.update(linux_vars)

    return vars
