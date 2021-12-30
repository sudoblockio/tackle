"""Test tackle.utils.paths."""
import pytest
from tackle.utils.paths import is_file, is_repo_url

FILE_FIXTURES = [
    ("file.yaml", True),
    ("file.yml", True),
    ("/foo.yaml/.file.yml", True),
    (".file.yml", True),
    ("file.json", True),
    ("file.hcl", False),
]


@pytest.mark.parametrize("file,is_file_result", FILE_FIXTURES)
def test_is_file(file, is_file_result):
    """Validate is_file regex."""
    assert is_file(file) == is_file_result


REPO_FIXTURES = [
    ("https://github.com/robcxyz/tackle-demo", True),
    ("github.com/robcxyz/tackle-demo", True),
    ("gitlab.com/robcxyz/tackle-demo", True),
    ("gitlab.com/robcxyz/tackle-demo/some/things", False),
    ("stuffhub.com/robcxyz/tackle-demo", False),
    ("robcxyz/tackle-demo", True),
    ("tests/utils", False),
    ("tests/utils/foo", False),
]


@pytest.mark.parametrize("repo,is_repo_result", REPO_FIXTURES)
def test_is_repo_url(repo, is_repo_result, change_dir_base):
    """Validate is_repo_url regex."""
    assert is_repo_url(repo) == is_repo_result
