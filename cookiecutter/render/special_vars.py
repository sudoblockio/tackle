"""Special variables to be used in rendering."""

import os
import platform

import distro

# from cookiecutter.model import Context


def get_vars(c):
    """Get special variables."""
    vars = {
        'cwd': os.getcwd(),
        'key': c.context_key,
        'this': c.output_dict,
        'system': platform.system(),
        'platform': platform.platform(),
        'release': platform.release(),
        'version': platform.version(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'calling_directory': c.calling_directory,
        'tackle_gen': c.tackle_gen,
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
