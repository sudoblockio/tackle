# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.github.hooks` modules."""
from tackle.main import tackle
import pytest
from github import Github, GithubException

try:
    g = Github()
    r = [r for r in g.get_user().get_repos()]
except GithubException:
    pytest.skip("Skipping github tests due to auth error.", allow_module_level=True)


def test_provider_github_hooks_repos(change_dir):
    """Test return repo info."""
    output = tackle(context_file='repo.yaml', no_input=True)
    assert output['repos'] > 1


if __name__ == '__main__':
    g = Github()
    x = g.get_user().get_repos()
