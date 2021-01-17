# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.docker.hooks` module."""
from tackle.main import tackle
import pytest
import os


@pytest.fixture()
def clean_outputs():
    """Clean outputs."""
    yield
    outputs = ["docker-stack.yml"]
    for o in outputs:
        if os.path.isfile(o):
            os.remove(o)


def test_provider_aws_docker_compose(change_dir, clean_outputs):
    """Verify the hook call works successfully."""
    tackle('.', context_file='compose.yaml')
    assert os.path.isfile("docker-stack.yml")
