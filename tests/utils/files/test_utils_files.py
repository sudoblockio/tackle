import pytest

from tackle.utils.files import read_config_file
from tackle.exceptions import ContextDecodingException, UnsupportedBaseFileTypeException


def test_read_config_file(change_curdir_fixtures):
    # assert read_config_file('documents.yaml') == [{'this': 'that'}, {'this': 'that'}]
    assert read_config_file('document.yaml')['this'] == 'that'
    assert read_config_file('file.yaml') == {'this': 'that'}
    assert read_config_file('ok.toml')['this'] == {'stuff': 'things'}

    with pytest.raises(ContextDecodingException):
        read_config_file('bad.json')

    with pytest.raises(UnsupportedBaseFileTypeException):
        read_config_file('bad.things')

    with pytest.raises(FileNotFoundError):
        read_config_file('bad')


def test_read_config_file_comments(change_curdir_fixtures):
    document = read_config_file('documents.yaml')
    assert document[0]['this'] == 'that'

    document = read_config_file('document.yaml')
    assert document['this'] == 'that'
