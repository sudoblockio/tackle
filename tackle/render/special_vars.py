"""Special variables to be used in rendering."""

import os
import platform

import csv

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context


def get_linux_distribution():
    """Return the equivalent of lsb_release -a."""
    if platform.system() == 'Linux':
        RELEASE_DATA = {}
        with open("/etc/os-release") as f:
            reader = csv.reader(f, delimiter="=")
            for row in reader:
                if row:
                    RELEASE_DATA[row[0]] = row[1]
        if RELEASE_DATA["ID"] in ["debian", "raspbian"]:
            with open("/etc/debian_version") as f:
                DEBIAN_VERSION = f.readline().strip()
            major_version = DEBIAN_VERSION.split(".")[0]
            version_split = RELEASE_DATA["VERSION"].split(" ", maxsplit=1)
            if version_split[0] == major_version:
                # Just major version shown, replace it with the full version
                RELEASE_DATA["VERSION"] = " ".join([DEBIAN_VERSION] + version_split[1:])
        return "{} {}".format(RELEASE_DATA["NAME"], RELEASE_DATA["VERSION"])
    else:
        return None


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
        'lsb_release': get_linux_distribution(),
        'calling_directory': context.calling_directory,
        'key': context.context_key,
        'this': dict(context.output_dict),
        'output': context.output_dict,
    }
    if platform.system() == 'Linux':
        # TODO: Replace - This shouldn't have to import distro
        # import distro
        # linux_id_name, linux_version, linux_codename = distro.linux_distribution(
        #     full_distribution_name=False
        # )
        # linux_vars = {
        #     'linux_id_name': linux_id_name,
        #     'linux_version': linux_version,
        #     'linux_codename': linux_codename,
        # }
        # vars.update(linux_vars)
        pass
    else:
        linux_vars = {
            'linux_id_name': None,
            'linux_version': None,
            'linux_codename': None,
        }
        vars.update(linux_vars)

    return vars
