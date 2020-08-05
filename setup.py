#!/usr/bin/env python
"""cookiecutter distutils configuration."""
import sys

from setuptools import setup

version = "2.0.0.2"

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

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
    'boto3>=1.14.0' 'google-api-python-client>=1.9',
    'google-api-python-client>=1.9',
    'azure-mgmt-compute>=13.0.0',
    'azure-mgmt-subscription>=0.6.0',
    'pyhcl>=0.4.4',
    'distro>=1.5.0',
    'rich>=3.3.0',
    'dopy>=0.3.7',
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
    packages=['cookiecutter'],
    package_dir={'cookiecutter': 'cookiecutter'},
    entry_points={'console_scripts': ['nukikata = cookiecutter.__main__:main']},
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
