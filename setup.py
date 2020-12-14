#!/usr/bin/env python
"""cookiecutter distutils configuration."""
import sys
import os
import re
from collections import defaultdict
from cookiecutter import __version__

from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

DEV_REQUIREMENTS = [
    'pytest',
    'pytest-cov',
    'pytest-mock',
    'freezegun',
    'ptyprocess',
]


def get_provider_requirements():
    """Get the provider requirements from each provider to allow extra requirements."""
    providers_dir = os.path.join(os.path.dirname(__file__), 'cookiecutter', 'providers')
    providers = os.listdir(providers_dir)
    provider_requirements = defaultdict(set)
    for p in providers:
        if p == '__init__.py':
            continue
        reqs_file = os.path.join(providers_dir, p, 'requirements.txt')
        if os.path.isfile(reqs_file):
            with open(reqs_file) as fp:
                for k in fp:
                    if k.strip() and not k.startswith('#'):
                        tags = set()
                        if ':' in k:
                            k, v = k.split(':')
                            tags.update(vv.strip() for vv in v.split(','))
                        tags.add(re.split('[<=>]', k)[0])

                        for _ in tags:
                            provider_requirements[p].add(k)

    provider_requirements['dev'] = set(DEV_REQUIREMENTS)
    provider_requirements['all'] = set(
        vv for v in provider_requirements.values() for vv in v
    )
    return provider_requirements


INSTALL_REQUIREMENTS = [
    'binaryornot>=0.4.4',
    'Jinja2<3.0.0',
    'click>=7.0',
    'poyo>=0.5.0',
    'jinja2-time>=0.2.0',
    'python-slugify>=4.0.0',
    'requests>=2.23.0',
    'PyInquirer>=1.0.3',
    'PyYAML>=5.3',
    'oyaml>=v1.0',
    'pyhcl>=0.4.4',
    'distro>=1.5.0',
    'rich>=3.3.0',
    'pydantic>=1.6.0',
]

if sys.argv[-1] == 'readme':
    print(readme)
    sys.exit()

setup(
    name='tackle-box',
    version=__version__,
    description=(
        'Plugins based DSL for creating workflows and generating code. '
        'Works with cookiecutter templates and extends them with conditional '
        'actions and custom actions that can be used modularly across repos.'
    ),
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Rob Cannon',
    author_email='robc.io.opensource@gmail.com',
    url='https://github.com/insight-infrastructure/tackle-box',
    # packages=['cookiecutter'],
    packages=find_packages(exclude=['tests*', 'logo*', 'docs*', '.github*']),
    package_dir={'cookiecutter': 'cookiecutter'},
    entry_points={'console_scripts': ['tackle = cookiecutter.__main__:main']},
    extras_require=get_provider_requirements(),
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
