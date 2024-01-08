#!/usr/bin/env python
import codecs
import os

from setuptools import find_packages, setup

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


INSTALL_REQUIREMENTS = [
    'Jinja2>3.0.0',
    'requests>=2.23.0',  # This would be needed if we allowed url sources
    'pydantic>=2.4.2',
    'pydantic-settings>2.0.0',
    'InquirerPy>=0.3.3',
    # 'ruamel.yaml>=0.17.0',
    'ruyaml==0.91.0',
    'rich>=12.6.0',
    'xdg==5.1.1',
]

# Add tomli only for Python 3.10
EXTRAS_REQUIRE = {':python_version == "3.10"': ['tomli>=1.0.0']}

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
    url='https://github.com/sudoblockio/tackle',
    packages=find_packages(exclude=['tests*', 'logo*', 'docs*', '.github*']),
    package_dir={'tackle': 'tackle'},
    entry_points={'console_scripts': ['tackle = tackle.cli:main']},
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=INSTALL_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    keywords=[
        "tackle",
        "tackle-box",
        "tacklebox",
        "tackle box",
        "Python",
        "projects",
        "Jinja2",
        "project templates",
        "cookiecutter",
        "skeleton",
        "scaffolding",
        "project directory",
        "package",
        "packaging",
        "kubernetes",
        "config file management",
        "configuration language",
        "declarative cli",
    ],
)
