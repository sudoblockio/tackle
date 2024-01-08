import os.path

import pytest

from tackle.utils.paths import find_hooks_dir_from_tests, is_file, is_repo_url


@pytest.mark.parametrize(
    "file,is_file_result",
    [
        ("file.yaml", True),
        ("file.yml", True),
        ("/foo.yaml/.file.yml", True),
        (".file.yml", True),
        ("file.json", True),
        ("file.hcl", False),
    ],
)
def test_utils_paths_is_file(file, is_file_result, mocker):
    """Validate is_file regex."""
    mocker.patch('os.path.isfile', return_value=True)
    assert is_file(file, None) == is_file_result


@pytest.mark.parametrize(
    "repo,is_repo_result",
    [
        ("https://github.com/robcxyz/tackle-demo", True),
        ("github.com/robcxyz/tackle-demo", True),
        ("gitlab.com/robcxyz/tackle-demo", True),
        ("gitlab.com/robcxyz/tackle-demo/some/things", False),
        ("stuffhub.com/robcxyz/tackle-demo", False),
        ("robcxyz/tackle-demo", True),
        ("tests/utils", False),
        ("tests/utils/foo", False),
    ],
)
def test_utils_paths_is_repo_url(repo, is_repo_result, cd_base_dir):
    """Validate is_repo_url regex."""
    assert is_repo_url(repo) == is_repo_result


@pytest.mark.parametrize(
    "input_path,expected_output",
    [
        ('.', lambda x: x is None),
        (
            os.path.join('fixtures', 'a-provider', 'tests'),
            lambda x: x.endswith('.hooks'),
        ),
        (os.path.join('..', '..', 'providers', 'tackle', 'tests'), lambda x: x is None),
        # (os.path.join('..', '..'), lambda x: x is None),  # Could be flakey
        # (tempfile.TemporaryDirectory(), lambda x: x is None),  # Not working...
    ],
)
def test_utils_paths_find_hooks_dir_from_tests(input_path, expected_output, cd):
    """
    When we are in certain paths, check we return the path to the hooks dir if we are
     not inside the tackle dir.
    """
    cd(input_path)
    output = find_hooks_dir_from_tests(os.path.abspath('.'))
    assert expected_output(output)
