# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.regions` module."""
from cookiecutter.main import cookiecutter


def test_operator_azure_regions(change_dir):
    """Verify the operator call works successfully."""
    context = cookiecutter('.')
    assert len(context['azs']) > 1
