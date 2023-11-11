import pytest

from tackle import tackle, exceptions


def test_hooks_model_config():
    output = tackle('model-config.yaml')
    assert output['call']['bar'] == 'baz'


def test_hooks_model_config_invalid_model():
    with pytest.raises(exceptions.MalformedHookFieldException):
        tackle('bad-model-config.yaml')