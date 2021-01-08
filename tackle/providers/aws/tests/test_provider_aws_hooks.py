# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.aws.hooks` module."""
from tackle.main import tackle
import pytest
import boto3
from botocore.exceptions import ClientError


try:
    sts = boto3.client('sts')
    sts.get_caller_identity()
except ClientError:
    pytest.skip("Skipping AWS tests due to auth error.", allow_module_level=True)


def test_provider_aws_hooks_regions(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='regions.yaml')
    assert len(context['azs']) > 1


def test_provider_aws_hooks_ec2_meta(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', no_input=True)
    assert len(context['instance_types']) > 1


def test_provider_aws_hooks_ec2_meta_instance_family(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='instance_family.yaml')

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 50


# SUPER LONG TEST - Out by default
# def test_provider_aws_hooks_ec2_meta_all_regions(change_dir):
#     """Verify the hook call works successfully."""
#     context = tackle('.', context_file='all_regions.yaml')
#
#     assert len(context['instance_types']) > 1
#     assert len(context['instance_types']) < 50


def test_provider_aws_hooks_azs_region(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='azs_region.yaml', no_input=True)

    assert len(context) > 1


def test_provider_aws_hooks_azs_regions(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='azs_regions.yaml', no_input=True)

    assert len(context) > 1
    assert len(context['azs']['us-east-1']) > 1
