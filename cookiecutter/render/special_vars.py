"""Special variables to be used in rendering."""

import os
import platform

import distro

import cookiecutter as cc


def get_vars(context_key=None, cc_dict=None):
    """Get special variables."""
    vars = {
        'cwd': os.getcwd(),
        'key': context_key,
        'this': cc_dict,
        'system': platform.system(),
        'platform': platform.platform(),
        'release': platform.release(),
        'version': platform.version(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'calling_directory': cc.main.calling_directory,  # noqa
        'cookiecutter_gen': cc.repository.cookiecutter_gen,  # noqa
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
