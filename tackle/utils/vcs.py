"""Helper functions for working with version control systems."""
import logging
import os
import subprocess
from shutil import which

from tackle.exceptions import (
    RepositoryCloneFailed,
    RepositoryNotFound,
    VCSNotInstalled,
    VersionNotFoundError,
)
from tackle.utils.prompts import prompt_and_delete
from tackle.utils.paths import make_sure_path_exists
from tackle.settings import settings
from tackle.utils.paths import work_in

logger = logging.getLogger(__name__)

BRANCH_ERRORS = [
    'error: pathspec',
    'unknown revision',
]


# def identify_repo(repo_url):
#     """Determine if `repo_url` should be treated as a URL to a git or hg repo.
#
#     Repos can be identified by prepending "hg+" or "git+" to the repo URL.
#
#     :param repo_url: Repo URL of unknown type.
#     :returns: ('git', repo_url), ('hg', repo_url), or None.
#     """
#     repo_url_values = repo_url.split('+')
#     if len(repo_url_values) == 2:
#         repo_type = repo_url_values[0]
#         if repo_type in ["git", "hg"]:
#             return repo_type, repo_url_values[1]
#         else:
#             raise UnknownRepoType
#     else:
#         if 'git' in repo_url:
#             return 'git', repo_url
#         elif 'bitbucket' in repo_url:
#             return 'hg', repo_url
#         else:
#             raise UnknownRepoType


# def prompt_and_delete(path, no_input=False):
#     """
#     Ask user if it's okay to delete the previously-downloaded file/directory.
#
#     If yes, delete it. If no, checks to see if the old version should be
#     reused. If yes, it's reused; otherwise, Tackle exits.
#
#     :param path: Previously downloaded zipfile.
#     :param no_input: Suppress prompt to delete repo and just delete it.
#     :return: True if the content was deleted
#     """
#     # Suppress prompt if called via API
#     if no_input:
#         ok_to_delete = True
#     else:
#         question = (
#             "You've downloaded {} before. Is it okay to delete and re-download it?"
#         ).format(path)
#
#         ok_to_delete = read_user_yes_no(question, 'no')
#
#     if ok_to_delete:
#         if os.path.isdir(path):
#             rmtree(path)
#         else:
#             os.remove(path)
#         return True
#     else:
#         ok_to_reuse = read_user_yes_no(
#             "Do you want to re-use the existing version?", 'yes'
#         )
#
#         if ok_to_reuse:
#             return False
#
#         sys.exit()


def clone(repo_url, checkout=None, clone_to_dir='.', no_input=False):
    """Clone a repo to the current directory.

    :param repo_url: Repo URL of unknown type.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param clone_to_dir: The directory to clone to.
                         Defaults to the current directory.
    :param no_input: Suppress all user prompts when calling via API.
    :returns: str with path to the new directory of the repository.
    """
    # Ensure that clone_to_dir exists
    clone_to_dir = os.path.expanduser(clone_to_dir)
    make_sure_path_exists(clone_to_dir)

    # identify the repo_type
    # repo_type, repo_url = identify_repo(repo_url)

    # check that the appropriate VCS for the repo_type is installed
    if not is_vcs_installed('git'):
        msg = "git is not installed."
        raise VCSNotInstalled(msg)

    repo_url = repo_url.rstrip('/')
    repo_name = os.path.split(repo_url)[1]
    repo_name = repo_name.split(':')[-1].rsplit('.git')[0]
    repo_dir = os.path.normpath(os.path.join(clone_to_dir, repo_name))
    logger.debug('repo_dir is {0}'.format(repo_dir))

    if os.path.isdir(repo_dir):
        clone = prompt_and_delete(repo_dir, no_input=no_input)
    else:
        clone = True

    if clone:
        try:
            subprocess.check_output(
                ['git', 'clone', repo_url],
                cwd=clone_to_dir,
                stderr=subprocess.STDOUT,
            )
            if checkout is not None:
                subprocess.check_output(
                    ['git', 'checkout', checkout],
                    cwd=repo_dir,
                    stderr=subprocess.STDOUT,
                )
        except subprocess.CalledProcessError as clone_error:
            output = clone_error.output.decode('utf-8')
            if 'not found' in output.lower():
                raise RepositoryNotFound(
                    'The repository {} could not be found, '
                    'have you made a typo?'.format(repo_url)
                )
            if any(error in output for error in BRANCH_ERRORS):
                raise RepositoryCloneFailed(
                    'The {} branch of repository {} could not found, '
                    'have you made a typo?'.format(checkout, repo_url)
                )
            raise

    return repo_dir


def is_vcs_installed(repo_type):
    """
    Check if the version control system for a repo type is installed.

    :param repo_type:
    """
    return bool(which(repo_type))


def get_default_branch(repo_path):
    """Get the default branch from a repo / provider."""
    cmd = "git remote show origin"
    with work_in(repo_path):
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
        )
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            for i in stdout.strip().splitlines():
                if i.startswith(b'  HEAD'):
                    return i.split()[2].decode("utf-8")
        else:
            raise ValueError("No idea why this would not work....")


def get_latest_release(repo_path):
    """Checkout the latest release."""
    cmd = "git ls-remote --tags --exit-code --refs origin"
    with work_in(repo_path):
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
        )
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            # last line is the latest release
            return stdout.strip().splitlines()[-1].decode('utf-8').split('/')[-1]
        elif p.returncode == 2:
            return None


def get_repo_version(repo_path):
    """Get the current repo version / branch."""
    with work_in(repo_path):
        with open('.git/HEAD') as f:
            ref = f.read()
    ref_list = ref.strip().split('/')
    if len(ref_list) == 1:
        return ref_list[0]
    return ref_list[2]


def checkout_version(repo_path, version):
    """Checkout a version / branch."""
    cmd = f"git checkout {version}"
    with work_in(repo_path):
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
        )
        stdout, stderr = p.communicate()

        if 'Your branch is behind' in str(stdout):
            cmd = 'git pull'
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True,
            )
            p.communicate()

        if p.returncode == 0:
            return
            # return stdout.strip()
        else:
            rough_repo = '/'.join(repo_path.split('/')[-2:])
            raise VersionNotFoundError(
                f"Could not find the version='{version}' for the repo {rough_repo}."
            ) from None


def parse_repo_ref(repo):
    """Parse the repo string into parts."""
    # If starts with https
    organization = None
    provider_name = None
    repo_prefix = None

    if repo.startswith('https://'):
        repo_parts = repo.split('/')
        repo_prefix = 'https://' + repo_parts[2]
        organization = repo_parts[3]
        provider_name = repo_parts[4]

    elif len(repo.split('/')) == 2:
        # Handle type robcxyz/tackle
        repo_parts = repo.split('/')
        repo_prefix = 'https://github.com'
        organization = repo_parts[0]
        provider_name = repo_parts[1]

    elif repo.split('.')[1].startswith('com'):
        # Handles type github.com/robcxyz/tackle
        # TODO: This condition can be tightened
        repo_parts = repo.split('/')
        repo_prefix = 'https://' + repo_parts[0]
        organization = repo_parts[1]
        provider_name = repo_parts[2]

    if not organization or not provider_name:
        # This should be found by now otherwise it is an invalid format
        # Should not happen as the regex that qualifies a repo shouldn't have passed
        raise ValueError

    repo_url = '/'.join([repo_prefix, organization, provider_name])
    return repo_url, organization, provider_name


def get_repo_source(repo: str, repo_version: str = None) -> str:
    """Clone a provider into the providers dir with checkout out the right version."""
    repo_url, organization, provider_name = parse_repo_ref(repo)
    # provider_dir = os.path.join(settings.provider_dir, organization, provider_name)
    org_dir = os.path.join(settings.provider_dir, organization)
    provider_dir = os.path.join(org_dir, provider_name)

    logger.debug(f"Repo {repo_url} found for org {organization}, name {provider_name}.")

    if not os.path.exists(provider_dir):
        # Clone if dir does not exist (new provider)
        clone(repo_url, clone_to_dir=org_dir)
    else:
        subprocess.check_output(
            ['git', 'fetch'],
            cwd=provider_dir,
            stderr=subprocess.STDOUT,
        )

    # Get the default branch of the repo
    # If a version is specified, then check that first
    version = get_repo_version(provider_dir)
    logger.debug(f"Version for {provider_name} equal to {version}.")

    if repo_version:
        if repo_version == 'latest':
            default_branch = get_default_branch(repo_path=provider_dir)
            checkout_version(repo_path=provider_dir, version=default_branch)
        else:
            checkout_version(repo_path=provider_dir, version=repo_version)
    else:
        latest_release = get_latest_release(repo_path=provider_dir)
        if version != latest_release and latest_release is not None:
            # Condition where we have a newer release from a repo that has a release
            checkout_version(repo_path=provider_dir, version=latest_release)
        elif latest_release is None:
            # Condition where we have a repo that has no release so we just pull latest
            default_branch = get_default_branch(repo_path=provider_dir)
            checkout_version(repo_path=provider_dir, version=default_branch)

    return provider_dir
