#!/usr/bin/env python
"""cookiecutter distutils configuration."""
import sys

from setuptools import setup, Command, find_packages
from textwrap import wrap
from typing import List

version = "2.0.0.3"

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()


class ListExtras(Command):
    """
    List all available extras.

    Registered as cmdclass in setup() so it can be called with
    ``python setup.py list_extras``.

    :param Command:
    """

    description = "List available extras"
    user_options = []  # type: List[str]

    def initialize_options(self):
        """Set default values for options."""

    def finalize_options(self):
        """Set final values for options."""

    # noinspection PyMethodMayBeStatic
    def run(self):
        """List extras."""
        print("\n".join(wrap(", ".join(EXTRAS_REQUIREMENTS.keys()), 100)))


amazon = [
    'boto3>=1.14.0',
]

azure = [
    'azure-mgmt-compute>=13.0.0',
    'azure-mgmt-subscription>=0.6.0',
]

digitalocean = [
    'dopy>=0.3.7',
]

google = [
    'google-api-python-client>=1.9',
]

vault = []

devel = [
    'pytest',
    'pytest-cov',
    'pytest-mock',
    'freezegun',
    'ptyprocess',
]

PROVIDERS_REQUIREMENTS = {
    'amazon': amazon,
    'google': google,
    'digitalocean': digitalocean,
}

EXTRAS_REQUIREMENTS = {
    # 'all': all,
}

# Make devel_all contain all providers + extras + unique
devel_all = list(
    set(
        devel
        + [req for req_list in EXTRAS_REQUIREMENTS.values() for req in req_list]
        + [req for req_list in PROVIDERS_REQUIREMENTS.values() for req in req_list]
    )
)

PACKAGES_EXCLUDED_FOR_ALL = []

# Those packages are excluded because they break tests (downgrading mock) and they are
# not needed to run our test suite.
PACKAGES_EXCLUDED_FOR_CI = [
    'apache-beam',
]


def is_package_excluded(package: str, exclusion_list: List[str]):
    """
    Checks if package should be excluded.

    :param package: package name (beginning of it)
    :param exclusion_list: list of excluded packages
    :return: true if package should be excluded
    """
    return any(
        [package.startswith(excluded_package) for excluded_package in exclusion_list]
    )


devel_all = [
    package
    for package in devel_all
    if not is_package_excluded(
        package=package, exclusion_list=PACKAGES_EXCLUDED_FOR_ALL
    )
]

devel_ci = [
    package
    for package in devel_all
    if not is_package_excluded(
        package=package,
        exclusion_list=PACKAGES_EXCLUDED_FOR_CI + PACKAGES_EXCLUDED_FOR_ALL,
    )
]

EXTRAS_REQUIREMENTS.update(
    {'all': devel_all, 'devel_ci': devel_ci,}
)

EXTRAS_REQUIREMENTS.update(PROVIDERS_REQUIREMENTS)

INSTALL_REQUIREMENTS = [
    'binaryornot>=0.4.4',
    'Jinja2<3.0.0',
    'click>=7.0',
    'poyo>=0.5.0',
    'jinja2-time>=0.2.0',
    'python-slugify>=4.0.0',
    'requests>=2.23.0',
    'MarkupSafe<2.0.0',
    'PyInquirer>=1.0.3',
    'PyYAML>=5.3',
    # 'ruamel.yaml>=0.16.0',
    'boto3>=1.14.0',
    'google-api-python-client>=1.9',
    'azure-mgmt-compute>=13.0.0',
    'azure-mgmt-subscription>=0.6.0',
    'pyhcl>=0.4.4',
    'distro>=1.5.0',
    'rich>=3.3.0',
    'dopy>=0.3.7',
    'pydantic>=1.6.0',
]

if sys.argv[-1] == 'readme':
    print(readme)
    sys.exit()

setup(
    name='nukikata',
    version=version,
    description=(
        'Fork of cookiecutter - https://github.com/cookiecutter/cookiecutter '
        'The most popular command-line utility to create projects from project '
        'templates, e.g. creating a Python package project from a '
        'Python package project template.'
    ),
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Fork by Rob Cannon',
    author_email='rob.cannon@insightinfrastructure.com',
    url='https://github.com/insight-infrastructure/nukikata',
    # packages=['cookiecutter'],
    packages=find_packages(exclude=['tests*', 'logo*', 'docs*', '.github*']),
    package_dir={'cookiecutter': 'cookiecutter'},
    entry_points={'console_scripts': ['nuki = cookiecutter.__main__:main']},
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=INSTALL_REQUIREMENTS,
    license='BSD',
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    keywords=[
        "cookiecutter",
        "Python",
        "projects",
        "project templates",
        "Jinja2",
        "skeleton",
        "scaffolding",
        "project directory",
        "package",
        "packaging",
    ],
)
