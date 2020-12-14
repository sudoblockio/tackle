# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.digitalocean.regions` module."""

import os
from tackle.main import tackle


def test_operator_digitalocean_regions(change_dir):
    """Verify DO azs."""
    output = tackle('.')
    assert len(output['azs']) > 1
