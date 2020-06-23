# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""

# from helpers import create_example_fixture, keys
# import os
#
# FIXTURES = ['checkbox_bad.yaml']
#
# example_app = create_example_fixture(os.path.join(os.path.dirname(__file__),
#                                                   'checkbox.py'))
#
# def test_checkbox(example_app):
#     # TODO: get psuedo terminal working to enter in commands
#     x = example_app.write(keys.ENTER)
#     print()
#     x = example_app.write(keys.ENTER)
#     x = example_app.write(keys.ENTER)
#     print()


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
