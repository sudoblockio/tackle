# -*- coding: utf-8 -*-

"""Tests dict rednering special variables."""
import os
from tackle.main import tackle


def test_special_variables(change_dir):
    """Verify Jinja2 time extension work correctly."""
    # monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = tackle('test-special-variables', no_input=True)

    assert output['calling_directory'] == os.path.dirname(__file__)
    assert os.path.basename(output['cwd']) == 'test-special-variables'
    assert len(output) > 12


# TODO: Would be cool if there was an easy way to dump the context without having
#  to type out the whole operator.
# def test_special_variables_debug(change_dir):
#     """Verify Jinja2 time extension work correctly."""
#     output = tackle('test-special-variables', no_input=True, context_file='debug.yaml')
#     assert output['debug']['type'] == 'pprint'
