# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.ec2_meta` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_aws_ec2_meta(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(context['nuki']['instance_types']) > 1


def test_operator_aws_ec2_meta_instance_family(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.',
        context_file='instance_family.yaml',
        # context_key='instance_family',
        no_input=True,
        output_dir=str(tmpdir),
    )

    assert len(context['instance_family']['instance_types']) > 1
    assert len(context['instance_family']['instance_types']) < 50
