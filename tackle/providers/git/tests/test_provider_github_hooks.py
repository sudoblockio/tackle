# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.github.hooks` modules."""
import os
from tackle.main import tackle


def test_provider_git_hooks_repos(change_dir):
    """Verify hook."""
    output = tackle('.', context_file='repo.yaml')
