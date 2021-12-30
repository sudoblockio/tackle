"""Test tackle.utils.vcs."""
import os
import pytest

from tackle.settings import settings
from tackle.utils.vcs import (
    parse_repo_ref,
    get_repo_version,
    get_default_branch,
    get_repo_source,
    # clone_to_dir,
    get_latest_release,
)

DEMO_INPUTS = [
    "https://github.com/robcxyz/tackle-demos",
    "github.com/robcxyz/tackle-demos",
    "robcxyz/tackle-demos",
]


@pytest.mark.parametrize("repo_input", DEMO_INPUTS)
def test_parse_repo_ref(repo_input):
    """Test parsing the repo reference."""
    repo_url, organization, provider_name = parse_repo_ref(repo_input)
    assert repo_url == "https://github.com/robcxyz/tackle-demos"
    assert organization == "robcxyz"
    assert provider_name == "tackle-demos"


DEMO_INPUTS = [
    ("https://github.com/robcxyz/tackle-demos", "main", "main"),
    ("github.com/robcxyz/tackle-demos", "latest", "main"),
    (
        "robcxyz/tackle-demos",
        "v0.0.1-alpha.1",
        "e11248f29c7e4ebcd04164be230f41513b576ffe",
    ),
]


@pytest.mark.parametrize("repo_input,repo_version,expected_version", DEMO_INPUTS)
def test_get_repo_source(
    tmp_move_tackle_dir, repo_input, repo_version, expected_version
):
    """Test getting the repo and cloning it to the providers dir returning the path."""
    get_repo_source(repo=repo_input, repo_version=repo_version)
    assert os.listdir(settings.provider_dir) == ['robcxyz']
    assert (
        get_repo_version(os.path.join(settings.provider_dir, 'robcxyz', 'tackle-demos'))
        == expected_version
    )


def test_get_repo_version(change_dir_base):
    """Test get_repo_version."""
    version = get_repo_version('.')
    assert len(version) > 3


def test_get_default_branch(change_dir_base):
    """Test getting the default branch of current repo."""
    branch = get_default_branch('.')
    assert branch == 'main'


def test_get_latest_release(change_dir_base):
    """Get the latest release in repo."""
    release = get_latest_release('.')
    assert len(release) > 4
