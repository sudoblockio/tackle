import os
import pytest

from tackle.settings import settings
from tackle.utils.vcs import (
    parse_repo_ref,
    get_repo_version,
    get_default_branch,
    get_repo_source,
    clone_to_dir,
    get_latest_release,
)
from tackle.exceptions import UnknownRepoType

DEMO_INPUTS = [
    "https://github.com/robcxyz/tackle-demos",
    "github.com/robcxyz/tackle-demos",
    "robcxyz/tackle-demos",
]


@pytest.mark.parametrize("repo_input", DEMO_INPUTS)
def test_parse_repo_ref(repo_input):
    repo_url, organization, provider_name = parse_repo_ref(repo_input)
    assert repo_url == "https://github.com/robcxyz/tackle-demos"
    assert organization == "robcxyz"
    assert provider_name == "tackle-demos"


def test_asssert_error_unknown_repo():
    with pytest.raises(UnknownRepoType):
        clone_to_dir('https://github.com/robcxyz/tackle-THINGS', 'foo')


DEMO_INPUTS = [
    ("https://github.com/robcxyz/tackle-demos", "main", "main"),
    ("github.com/robcxyz/tackle-demos", "latest", "main"),
    ("robcxyz/tackle-demos", "v0.0.1-alpha.1", "e11248f29c7e4ebcd04164be230f41513b576ffe"),
]


@pytest.mark.parametrize("repo_input,repo_version,expected_version", DEMO_INPUTS)
def test_get_repo_source(tmp_move_tackle_dir, repo_input, repo_version, expected_version):
    get_repo_source(repo=repo_input, repo_version=repo_version)
    assert os.listdir(settings.provider_dir) == ['robcxyz']
    assert get_repo_version(os.path.join(settings.provider_dir, 'robcxyz', 'tackle-demos')) == expected_version


def test_get_repo_version(change_dir_base):
    version = get_repo_version('.')
    assert len(version) > 3


def test_get_default_branch(change_dir_base):
    branch = get_default_branch('.')
    assert branch == 'main'


def test_get_latest_release(change_dir_base):
    release = get_latest_release('.')
    assert len(release) > 4
