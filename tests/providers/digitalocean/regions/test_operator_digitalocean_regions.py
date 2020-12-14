# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.digitalocean.regions` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_digitalocean_regions(change_dir):
    """Verify DO azs."""
    output = cookiecutter('.')
    assert len(output['azs']) > 1
