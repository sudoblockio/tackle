import pytest

from tackle import exceptions, tackle

# # TODO: Support config params which interfere with parser.
# #  https://github.com/sudoblockio/tackle/issues/219
# #  https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra
# def test_hooks_model_config_extra_allow():
#     """Example of model_config parameter which does interfere with the parser."""
#     output = tackle('extra-allow.yaml')
#
#     assert output['call']['bar'] == 'baz'


def test_hooks_model_config_str_to_upper():
    """Example of model_config parameter which does not interfere with the parser."""
    output = tackle('str-to-upper.yaml')

    assert output['call']['foo'] == 'BAZ'


def test_hooks_model_config_invalid_model():
    with pytest.raises(exceptions.MalformedHookFieldException):
        tackle('bad-model-config.yaml')
