# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.github.hooks` modules."""
import os
from tackle.main import tackle


def test_provider_github_hooks_repos(change_dir):
    """Test return repo info."""
    output = tackle('.', context_file='repo.yaml')
    assert output['repos'] > 1
