# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""

import yaml
import os
import shutil

from cookiecutter import prompt

FIXTURES = ['checkbox_bad.yaml']


def checkbox():
    """Test mo stuff."""
    fixture = 'checkbox_bad.yaml'
    with open(fixture, 'r') as f:
        context = yaml.load(f, Loader=yaml.FullLoader)

    if os.path.exists('./best_eva'):
        shutil.rmtree('best_eva')

    out_dict = prompt.prompt_for_config(context)
    return out_dict


if __name__ == '__main__':
    checkbox()

# class TestPromptHookDicts(object):
#     """Class to test all the dict input objects."""
#
#     @pytest.mark.parametrize("input_dicts,invalid", FIXTURES)
#     def test_hook_checkbox(self, monkeypatch):
#         """Verify `prompt_for_config` call `read_user_variable` on dict request."""
#
#         monkeypatch.setattr(
#             'cookiecutter.prompt.read_user_dict',
#             lambda var, default: {"key": "value", "integer": 37},
#         )
#         context = {'cookiecutter': {'details': {}}}
#
#         cookiecutter_dict = prompt.prompt_for_config(context)
#         assert cookiecutter_dict == {'details': {'key': u'value', 'integer': 37}}
