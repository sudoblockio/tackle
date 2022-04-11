import pytest

from tackle import exceptions, main


def test_should_raise_error_if_variable_does_not_exist(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownTemplateVariableException):
        main.tackle('unknown-variable.yaml')
