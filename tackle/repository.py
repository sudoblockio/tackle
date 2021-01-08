"""Tackle repository functions."""
import os
import re

from tackle.exceptions import RepositoryNotFound, ContextFileNotFound
from tackle.utils.vcs import clone
from tackle.utils.zipfile import unzip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Mode, Source, Settings


def is_git_repo(value):
    """Return True if value is a git repo."""
    GIT_REPO_REGEX = re.compile(
        r"""
    # something like git:// ssh:// file:// etc.
    (((git\+)?(https?):(//)?)
     |                                      # or
     (git@[\w\.]+)                          # something like git@...
    )
    """,
        re.VERBOSE,
    )
    return bool(GIT_REPO_REGEX.match(value))


def is_repo_url(value):
    """Return True if value is a repository URL."""
    REPO_REGEX = re.compile(
        r"""
    # something like git:// ssh:// file:// etc.
    ((((git|hg)\+)?(git|ssh|file|https?):(//)?)
     |                                      # or
     (\w+@[\w\.]+)                          # something like user@...
    )
    """,
        re.VERBOSE,
    )
    return bool(REPO_REGEX.match(value))


def is_zip_file(value):
    """Return True if value is a zip file."""
    return value.lower().endswith('.zip')


def expand_abbreviations(template, abbreviations):
    """Expand abbreviations in a template name.

    :param template: The project template name.
    :param abbreviations: Abbreviation definitions.
    """
    if template in abbreviations:
        return abbreviations[template]

    # Split on colon. If there is no colon, rest will be empty
    # and prefix will be the whole template
    prefix, sep, rest = template.partition(':')
    if prefix in abbreviations:
        return abbreviations[prefix].format(rest)

    return template


CONTEXT_FILE_DICT = {
    'cookiecutter': [
        'cookiecutter.json',
        'cookiecutter.yaml',
        'cookiecutter.yml',
        'cookiecutter.hcl',
    ],
    'tackle': [
        '.tackle.yaml',
        '.tackle.yml',
        '.tackle.json',
        '.tackle.hcl',
        'tackle.yaml',
        'tackle.yml',
        'tackle.json',
        'tackle.hcl',
    ],
}

ALL_VALID_CONTEXT_FILES = (
    CONTEXT_FILE_DICT['cookiecutter'] + CONTEXT_FILE_DICT['tackle']
)


def determine_tackle_generation(context_file: str) -> str:
    """Determine the tackle generation."""
    if context_file in CONTEXT_FILE_DICT['cookiecutter']:
        return 'cookiecutter'
    else:
        return 'tackle'


def repository_has_tackle_file(repo_directory: str, context_file=None):
    """Determine if `repo_directory` contains a `cookiecutter.json` file.

    :param repo_directory: The candidate repository directory.
    :param context_file: eg. `tackle.yaml`.
    :return: The path to the context file
    """
    repo_directory_exists = os.path.isdir(repo_directory)
    if context_file:
        # The supplied context file exists
        context_file = os.path.join(os.path.abspath(repo_directory), context_file)
        if os.path.isfile(context_file):
            return context_file
        else:
            raise ContextFileNotFound(
                f"Can't find supplied context_file at {context_file}"
            )

    if repo_directory_exists:
        # Check for valid context files as default
        for f in ALL_VALID_CONTEXT_FILES:
            if os.path.isfile(os.path.join(repo_directory, f)):
                return f
    else:
        return None


def update_source(source: 'Source', settings: 'Settings', mode: 'Mode') -> 'Source':
    """
    Locate the repository directory from a template reference.

    Applies repository abbreviations to the template reference.
    If the template refers to a repository URL, clone it.
    If the template is a path to a local repository, use it.

    :param template: A directory containing a project template directory,
        or a URL to a git repository.
    :param abbreviations: A dictionary of repository abbreviation
        definitions.
    :param clone_to_dir: The directory to clone the repository into.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param password: The password to use when extracting the repository.
    :param directory: Directory within repo where cookiecutter.json lives.
    :return: A tuple containing the cookiecutter template directory, and
        a boolean descriving whether that directory should be cleaned up
        after the template has been instantiated.
    :raises: `RepositoryNotFound` if a repository directory could not be found.
    """
    source.template = expand_abbreviations(source.template, settings.abbreviations)
    if is_zip_file(source.template):
        unzipped_dir = unzip(
            zip_uri=source.template,
            is_url=is_repo_url(source.template),
            clone_to_dir=settings.tackle_dir,
            no_input=mode.no_input,
            password=source.password,
        )
        repository_candidates = [unzipped_dir]
        source.cleanup = True
    elif is_repo_url(source.template):
        cloned_repo = clone(
            repo_url=source.template,
            checkout=source.checkout,
            clone_to_dir=settings.tackle_dir,
            no_input=mode.no_input,
        )
        repository_candidates = [cloned_repo]
        source.cleanup = False
    else:
        repository_candidates = [
            source.template,
            os.path.join(settings.tackle_dir, source.template),
        ]
        source.cleanup = False

    if source.directory:
        repository_candidates = [
            os.path.join(s, source.directory) for s in repository_candidates
        ]

    for repo_candidate in repository_candidates:
        source.context_file = repository_has_tackle_file(
            repo_candidate, source.context_file
        )
        if not source.context_file:
            # Means that no valid context file has been found or provided
            continue
        else:
            source.repo_dir = os.path.abspath(repo_candidate)
            source.template_name = os.path.basename(os.path.abspath(repo_candidate))
            source.tackle_gen = determine_tackle_generation(source.context_file)
            return source

    raise RepositoryNotFound(
        'A valid repository for "{}" could not be found in the following '
        'locations:\n{}'.format(source.template, '\n'.join(repository_candidates))
    )
