import logging
import os
import subprocess
from shutil import which

from tackle import exceptions
from tackle.settings import settings
from tackle.utils.paths import make_sure_path_exists, work_in

logger = logging.getLogger(__name__)


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
        if provider_name.endswith('.git'):
            provider_name = provider_name[:-4]

    elif repo.startswith('git@'):
        # Handle SSH format
        repo_parts = repo.split(':')
        host_parts = repo_parts[0].split('@')
        repo_prefix = 'https://' + host_parts[1]
        path_parts = repo_parts[1].split('/')
        organization = path_parts[0]
        provider_name = path_parts[1]
        if provider_name.endswith('.git'):
            provider_name = provider_name[:-4]

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
        raise exceptions.GenericGitException(f'The repo={repo} was not parsed properly')

    repo_url = '/'.join([repo_prefix, organization, provider_name])
    return repo_url, organization, provider_name


def run_command(command: str) -> subprocess.Popen:
    """Wrapper for subprocess."""
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True,
    )
    return p


def git_clone(repo_url):
    """Git clone a repo."""
    logger.debug(f'Cloning url=`{repo_url}`')
    cmd = f'git clone {repo_url}'
    p = run_command(cmd)
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        return
    if 'not found' in str(stderr):
        raise exceptions.RepositoryNotFound(
            f'The repository {repo_url} could not be found, have you made a typo?'
        )
    raise exceptions.GenericGitException(f'Error running {cmd}\n{str(stderr)}')


def git_checkout(version: str):
    """Git checkout a tag."""
    cmd = f"Checkout version={version}."
    logger.debug(cmd)
    p = run_command(f"git checkout {version}")
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        return
    if f"Already on '{version}'" in str(stderr):
        return
    if stderr:
        # Don't know how this could happen
        raise exceptions.VersionNotFoundError(f'Error running {cmd}\n{str(stderr)}')


def git_stash():
    cmd = 'git stash --include-untracked'
    p = run_command(cmd)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise exceptions.GenericGitException(
            f'Error running {cmd}\n{str(stderr)}\n{os.listdir()}\n{os.path.abspath(".")}'
        )


def git_pull(branch: str, provider_dir: str = None):
    cmd = f'git pull origin {branch}'
    p = run_command(cmd)
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        return
    if stderr:
        raise exceptions.GenericGitException(
            f'Error running {cmd}\n{str(stderr)} in {provider_dir}'
        )


def get_default_branch():
    """Get the default branch from the local git repo."""
    cmd = "git branch -vv"
    p = run_command(cmd)
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        for i in stdout.decode("utf-8").strip().splitlines():
            if 'origin/' in i:
                return i.split('/')[1].split(':')[0].split(']')[0]
        else:
            raise ValueError("No idea why this would not work....")
    else:
        raise exceptions.GenericGitException(f'Error running {cmd}\n{str(stderr)}')


def get_git_tags():
    """Run the git command to get already fetched tags - does not make remote call."""
    p = run_command("git tag")
    stdout, stderr = p.communicate()
    tags = stdout.decode('utf-8').strip().split('\n')
    if tags[0] == '':
        # No releases
        return []
    return tags


def get_latest_release_from_remote():
    """Get the latest release from the remote."""
    cmd = "git ls-remote --tags --exit-code --refs origin"
    p = run_command(cmd)
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        # last line is the latest release
        return stdout.strip().splitlines()[-1].decode('utf-8').split('/')[-1]
    elif p.returncode == 2:
        # This indicates there is no release in the remote
        return


def get_repo(
    repo_url: str,
    org_dir: str,
    provider_dir: str,
    version: str | None,
    latest: bool | None,
):
    """
    For new providers, we need to clone the provider and check if there is a release
     use that release.
    """
    make_sure_path_exists(os.path.expanduser(org_dir))
    with work_in(org_dir):
        git_clone(repo_url)
    with work_in(provider_dir):
        if version:
            git_checkout(version)
        elif latest:
            # Already on latest
            return
        else:
            latest_release = get_latest_release_from_remote()
            if latest_release is not None:
                git_checkout(latest_release)


def get_version(provider_dir: str, version: str):
    """
    Do git checkout and if there is an error, do a git pull and try to checkout again,
     this time raising an error if the version does not exist.
    """
    with work_in(provider_dir):
        logger.debug(f"Checking out version={version}.")
        git_stash()
        p = run_command(f"git checkout {version}")
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            return
        elif 'did not match any file(s) known to git' in str(
            stderr
        ) or 'Your branch is behind' in str(stdout):
            default_branch = get_default_branch()
            git_pull(default_branch)
            git_checkout(version)


def get_latest(provider_dir: str):
    """Git pull and checkout the default branch."""
    with work_in(provider_dir):
        git_stash()
        default_branch = get_default_branch()
        git_pull(default_branch, provider_dir)
        git_checkout(default_branch)


def get_last_release(provider_dir: str):
    """Git pull and then check for the most recent tag to checkout."""
    with work_in(provider_dir):
        git_stash()
        default_branch = get_default_branch()
        git_pull(default_branch)
        tags = get_git_tags()
        if len(tags) != 0:
            git_checkout(tags[-1])
        else:
            git_checkout(default_branch)


def get_repo_source(repo: str, version: str | None, latest: bool | None) -> str:
    """Clone a provider into the providers dir with checkout out the right version."""
    # Check if git is installed
    if not bool(which('git')):
        raise exceptions.VCSNotInstalled("git is not installed. Exiting...")
    # Split up the repo string
    repo_url, organization, provider_name = parse_repo_ref(repo)
    org_dir = os.path.join(settings.providers_dir, organization)
    provider_dir = os.path.join(org_dir, provider_name)

    logger.debug(f"Getting repo={repo_url} org={organization} name={provider_name}")

    if not os.path.exists(provider_dir):
        # New provider
        get_repo(
            repo_url=repo_url,
            org_dir=org_dir,
            provider_dir=provider_dir,
            version=version,
            latest=latest,
        )
    elif version is not None:
        get_version(provider_dir=provider_dir, version=version)
    elif latest:
        get_latest(provider_dir=provider_dir)
    else:
        get_last_release(provider_dir=provider_dir)

    return provider_dir
