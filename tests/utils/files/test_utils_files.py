from typing import Type

import pytest

from tackle import exceptions
from tackle.utils.files import read_config_file

READ_CONFIG_FILE_FIXTURES: list[tuple[str, dict | str]] = [
    # file,expected_output
    ('document.yaml', {'this': 'that'}),
    ('ok.yaml', {'this': 'that'}),
    ('ok.toml', {'this': {'stuff': 'things'}}),
    ('ok.json', {'this': {'stuff': 'things'}}),
]


@pytest.mark.parametrize('file,expected_output', READ_CONFIG_FILE_FIXTURES)
def test_utils_files_read_config_file_parameterized(file, expected_output):
    """Check that we can read various file types."""
    output = read_config_file(file)
    assert output == expected_output


def test_utils_files_read_config_file_documents():
    """Check when the yaml is a separated document (ie has `---` it is read as list."""
    document = read_config_file('documents.yaml')
    assert document[0]['this'] == 'that'


FILES_EXCEPTIONS: list[tuple[str, Type[Exception]]] = [
    ('double-braces.yaml', exceptions.FileLoadingException),
    ('bad.json', exceptions.FileLoadingException),
    ('bad.yaml', exceptions.FileLoadingException),
    ('bad.toml', exceptions.FileLoadingException),
    ('bad.things', exceptions.UnsupportedBaseFileTypeException),
    ('bad', exceptions.TackleFileNotFoundError),
]


@pytest.mark.parametrize('file,exception', FILES_EXCEPTIONS)
def test_utils_files_exceptions(file, exception):
    with pytest.raises(exception):
        read_config_file(file)
