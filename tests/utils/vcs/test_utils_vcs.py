import os
import shutil
from contextlib import contextmanager

import pytest

from tackle import exceptions
from tackle.settings import settings
from tackle.utils.paths import work_in
from tackle.utils.vcs import (
    get_default_branch,
    get_git_tags,
    get_repo,
    get_repo_source,
    parse_repo_ref,
    run_command,
)


@pytest.mark.parametrize(
    "repo_input",
    [
        "robcxyz/tackle-demos",
        "https://github.com/robcxyz/tackle-demos",
        "https://github.com/robcxyz/tackle-demos.git",
        "github.com/robcxyz/tackle-demos",
        'git@gitlab.com:robcxyz/tackle-demos.git',
        'git@github.com:robcxyz/tackle-demos.git',
    ],
)
def test_parse_repo_ref(repo_input):
    """Test parsing the repo reference."""
    _, organization, provider_name = parse_repo_ref(repo_input)

    assert organization == "robcxyz"
    assert provider_name == "tackle-demos"


@pytest.mark.slow
@pytest.mark.parametrize(
    "fixture,assertion",
    [
        ('tackle-fixture-released', lambda x: x == 'main'),
        ('tackle-fixture-unreleased', lambda x: x == 'main'),
    ],
)
def test_vcs_get_default(get_local, fixture, assertion):
    """Test getting the default branch of current repo."""
    with work_in(get_local(fixture)):
        branch = get_default_branch()

    assert assertion(branch)


@pytest.mark.parametrize(
    "fixture,assertion",
    [
        # ('tackle-fixture-released', lambda x: x[-1].startswith('v')),
        ('tackle-fixture-unreleased', lambda x: not x),
    ],
)
def test_vcs_get_git_tags_released(get_local, fixture, assertion):
    with work_in(get_local(fixture)):
        tags = get_git_tags()

    assert assertion(tags)


@pytest.fixture
def get_local():
    """
    We need a local set of fixtures so we can test how providers react when they exist
     already. So we just clone them locally and ignore them.
    """

    def f(fixture: str):
        if not os.path.isdir(os.path.join(fixture, '.git')):
            p = run_command(f'git clone https://github.com/robcxyz/{fixture}')
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                raise Exception(f"Error test setup clone \n{stdout}\n{stderr}")
        return fixture

    return f


@pytest.fixture()
def setup_tmp(tmp_path, get_local):
    @contextmanager
    def f(fixture: str = None):
        old_value = settings.providers_dir
        settings.providers_dir = str(tmp_path)
        try:
            if fixture is not None:
                get_local(fixture)
                shutil.copytree(fixture, os.path.join(tmp_path, 'robcxyz', fixture))
            yield str(tmp_path)
        finally:
            settings.providers_dir = old_value

    return f


def get_repo_version(repo_path):
    """Get the current repo version / branch."""
    with work_in(repo_path):
        with open('.git/HEAD') as f:
            ref = f.read()
    ref_list = ref.strip().split('/')
    if len(ref_list) == 1:
        return ref_list[0]
    return ref_list[2]


def _get_current_branch(repo_path):
    with work_in(repo_path):
        # This gets branch
        p = run_command('git rev-parse --abbrev-ref HEAD')
        stdout, stderr = p.communicate()
        if b'HEAD' not in stdout:
            return stdout.decode('utf-8').strip()
        # This gets tag
        p = run_command('git describe --tags --abbrev=0')
        stdout, _ = p.communicate()
        if p.returncode == 0:
            return stdout.decode('utf-8').strip()
        # Return None if tag is not there
        return None


@pytest.mark.slow
@pytest.mark.parametrize(
    "fixture,kwargs,assertion",
    [
        (
            'tackle-fixture-released',
            {'version': None, 'latest': None},
            lambda x: x.startswith('v'),
        ),
        (
            'tackle-fixture-released',
            {'version': None, 'latest': True},
            lambda x: x == 'main',
        ),
        (
            'tackle-fixture-released',
            {'version': 'v0.1.2', 'latest': None},
            lambda x: x == 'v0.1.2',
        ),
        (
            'tackle-fixture-unreleased',
            {'version': None, 'latest': None},
            lambda x: x == 'main',
        ),
        (
            'tackle-fixture-unreleased',
            {'version': None, 'latest': True},
            lambda x: x == 'main',
        ),
    ],
)
def test_utils_vcs_get_repo_source(setup_tmp, fixture, kwargs, assertion):
    """
    Using the fixtures so that we can control the specific version that would exist in
     the providers dir (ie unreleased or versions behind), set up the tests in a tmp dir
     and then after getting the source, check the resulting version.
    """
    with setup_tmp(fixture):
        repo_path = get_repo_source(repo=f'robcxyz/{fixture}', **kwargs)
        result_version = _get_current_branch(repo_path)

    assert repo_path.endswith(fixture)
    assert assertion(result_version)


@pytest.mark.slow
@pytest.mark.parametrize(
    "fixture,latest,version,assertion",
    [
        ('tackle-fixture-released', None, None, lambda x: x.startswith('v')),
        ('tackle-fixture-released', True, None, lambda x: x == 'main'),
        ('tackle-fixture-released', None, 'v0.1.2', lambda x: x == 'v0.1.2'),
        ('tackle-fixture-unreleased', None, None, lambda x: x == 'main'),
        ('tackle-fixture-unreleased', True, None, lambda x: x == 'main'),
    ],
)
def test_utils_vcs_get_repo(setup_tmp, fixture, latest, version, assertion):
    """Using the remote fixtures, test that we can get a brand new source."""
    with setup_tmp() as tmp_dir:
        org_dir = os.path.join(tmp_dir, 'robcxyz')
        provider_dir = os.path.join(org_dir, fixture)
        get_repo(
            repo_url=f'https://github.com/robcxyz/{fixture}',
            org_dir=org_dir,
            provider_dir=provider_dir,
            version=version,
            latest=latest,
        )
        result_version = _get_current_branch(provider_dir)

    assert assertion(result_version)


@pytest.mark.slow
@pytest.mark.parametrize(
    "fixture,copy,version,exception",
    [
        ('tackle-fixture-released', False, 'NO_EXIST', exceptions.VersionNotFoundError),
        ('tackle-fixture-released', True, 'NO_EXIST', exceptions.VersionNotFoundError),
        (
            'NO_EXIST',
            False,
            None,
            (exceptions.RepositoryNotFound, exceptions.GenericGitException),
        ),
    ],
)
def test_utils_vcs_exceptions_new_repo(setup_tmp, fixture, copy, version, exception):
    """Test exceptions where the repo does not exist in providers"""
    with pytest.raises(exception):
        with setup_tmp(fixture if copy else None):
            get_repo_source(f'robcxyz/{fixture}', version, None)
