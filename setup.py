#!/usr/bin/env python
"""Tackle distutils configuration."""
import sys
import os
import re
from collections import defaultdict
import codecs

from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()


def _read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    """Get the version from the __version__ file in the tackle dir."""
    for line in _read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def parse_requirements_file(reqs_file, provider_requirements, key):
    """
    Parse a requirements file and update the provider_requirements dict.

    :param reqs_file: Path to requirements file
    :param provider_requirements: A default dict with keys for `extras_require` and value
        as set of requirements.
    :param key: Key for installing `extras_require`.
    :return: Response of request in a dict

    """
    with open(reqs_file) as fp:
        for k in fp:
            if k.strip() and not k.startswith('#'):
                tags = set()
                if ':' in k:
                    k, v = k.split(':')
                    tags.update(vv.strip() for vv in v.split(','))
                tags.add(re.split('[<=>]', k)[0])

                for _ in tags:
                    provider_requirements[key].add(k)


def get_provider_requirements():
    """Get the provider requirements from each provider to allow extra requirements."""
    providers_dir = os.path.join(os.path.dirname(__file__), 'tackle', 'providers')
    providers = os.listdir(providers_dir)
    provider_requirements = defaultdict(set)
    for p in providers:
        if p == '__init__.py':
            continue
        reqs_file = os.path.join(providers_dir, p, 'requirements.txt')
        if os.path.isfile(reqs_file):
            parse_requirements_file(reqs_file, provider_requirements, p)
    parse_requirements_file('requirements-dev.txt', provider_requirements, 'dev')
    provider_requirements['all'] = set(
        vv for v in provider_requirements.values() for vv in v
    )
    return provider_requirements


INSTALL_REQUIREMENTS = [
    'Jinja2>3.0.0',
    # 'requests>=2.23.0',  # This would be needed if we allowed url sources
    'pydantic>=1.8.0',
    'InquirerPy>=0.3.3',
    'ruamel.yaml>=0.17.0',
    'rich>=12.6.0',
    'xdg==5.1.1',
]

if sys.argv[-1] == 'readme':
    print(readme)
    sys.exit()

setup(
    name='tackle',
    version=get_version(os.path.join('tackle', '__init__.py')),
    description=(
        'Tackle is a declarative DSL for building modular workflows and code '
        'generators. Tool is plugins based and can easily be extended by writing '
        'additional hooks or importing external providers that can be turned into a '
        'self documenting CLI, all out of yaml, json, toml.'
    ),
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Rob Cannon',
    author_email='robc.io.opensource@gmail.com',
    url='https://github.com/robcxyz/tackle',
    packages=find_packages(exclude=['tests*', 'logo*', 'docs*', '.github*']),
    package_dir={'tackle': 'tackle'},
    entry_points={'console_scripts': ['tackle = tackle.cli:main']},
    extras_require=get_provider_requirements(),
    include_package_data=True,
    python_requires='>=3.7',
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    keywords=[
        "cookiecutter",
        "tackle",
        "tackle-box",
        "tacklebox",
        "tackle box",
        "Python",
        "projects",
        "project templates",
        "Jinja2",
        "skeleton",
        "scaffolding",
        "project directory",
        "package",
        "packaging",
        "kubernetes",
    ],
)
