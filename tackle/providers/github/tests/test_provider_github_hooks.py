# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.github.hooks` modules."""
from tackle.main import tackle


def test_provider_github_hooks_repos(change_dir):
    """Test return repo info."""
    output = tackle(context_file='repo.yaml', no_input=True)
    assert len(output['repos']) > 1


def test_provider_github_hooks_releases(change_dir):
    """Test return repo info."""
    output = tackle(context_file='releases.yaml', no_input=True)
    assert "1.7.1" in output['repos']
