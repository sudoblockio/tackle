#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""cookiecutter distutils configuration."""

import os
import io
import sys

from setuptools import setup

version = "1.7.2.7"

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

with io.open('README.md', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = [
    'binaryornot>=0.4.4',
    'Jinja2<3.0.0',
    'click>=7.0',
    'poyo>=0.5.0',
    'jinja2-time>=0.2.0',
    'python-slugify>=4.0.0',
    'requests>=2.23.0',
    'six>=1.10',
    'MarkupSafe<2.0.0',
    'PyInquirer>=1.0.3',
    'PyYAML>=5.3',
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
    author='Original Author - Audrey Roy, Fork by Rob Cannon',
    author_email='rob.cannon@insightinfrastructure.com',
    url='https://github.com/insight-infrastructure/nukikata',
    packages=['cookiecutter'],
    package_dir={'cookiecutter': 'cookiecutter'},
    entry_points={'console_scripts': ['nukikata = cookiecutter.__main__:main']},
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=requirements,
    extras_require={':python_version<"3.3"': ['whichcraft>=0.4.0']},
    license='BSD',
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development",
    ],
    keywords=(
        'cookiecutter, Python, projects, project templates, Jinja2, '
        'skeleton, scaffolding, project directory, setup.py, package, '
        'packaging, insight, insight data science, insight infrastructure, '
        'cli'
    ),
)
