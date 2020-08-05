# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.ec2_meta` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_aws_ec2_meta(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(context['instance_types']) > 1


def test_operator_aws_ec2_meta_instance_family(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='instance_family.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 50


# def test_operator_aws_ec2_meta_all_regions(monkeypatch, tmpdir):
#     """Verify the operator call works successfully."""
#     monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
#
#     context = cookiecutter(
#         '.', context_file='all_regions.yaml', no_input=True, output_dir=str(tmpdir),
#     )
#
#     assert len(context['instance_types']) > 1
#     assert len(context['instance_types']) < 50
