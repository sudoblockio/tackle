# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""

# import pytest

from cookiecutter import prompt


class TestPromptDicts(object):
    """Class to test all the dict input objects."""

    def test_prompt_for_config_dict(self, monkeypatch):
        """Verify `prompt_for_config` call `read_user_variable` on dict request."""
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_dict',
            lambda var, default: {"key": "value", "integer": 37},
        )
        context = {'cookiecutter': {'details': {}}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {'details': {'key': u'value', 'integer': 37}}
