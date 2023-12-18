import pytest

from tackle import exceptions
from tackle.context import Context, Data, Source
from tackle.factory import new_data


@pytest.fixture()
def patch_extract_base_file(mocker):
    mock = mocker.patch(
        'tackle.factory.extract_base_file',
        autospec=True,
        return_value={},
    )
    yield mock
    assert mock.called


def test_factory_data_new_data():
    data = new_data(context=Context(source=Source(file='tackle.yaml')))
    assert data.raw_input['stuff'] == 'things'


def test_factory_data_new_data_overrides_str(patch_extract_base_file):
    """String `overrides` should be a ref to a file."""
    data = new_data(context=Context(), overrides='some-override.yaml')
    assert data.overrides['stuff'] == 'things'


def test_factory_data_new_data_overrides_dict(patch_extract_base_file):
    """Dict `overrides` should be read as is."""
    data = new_data(context=Context(), overrides={'stuff': 'things'})
    assert data.overrides['stuff'] == 'things'


def test_factory_data_new_data_existing_data_dict(patch_extract_base_file):
    """Should be able to exiting data as a dict."""
    data = new_data(context=Context(), existing_data={'stuff': 'things'})
    assert data.existing['stuff'] == 'things'


def test_factory_data_new_data_existing_data_str_file(patch_extract_base_file):
    """Should be able to exiting data as a dict."""
    data = new_data(context=Context(), existing_data='some-override.yaml')
    assert data.existing['stuff'] == 'things'


def test_factory_data_new_data_existing_data_str_exception():
    """Should be able to exiting data as a dict."""
    with pytest.raises(exceptions.TackleFileNotFoundError):
        new_data(context=Context(), existing_data='does-not-exist')


def test_factory_data_new_data_existing_data_from_data(patch_extract_base_file):
    """Dict `overrides` should be read as is."""
    external_data = Data(public={'stuff': 'things'})
    data = new_data(
        context=Context(),
        existing_data={'stuff': 'more things', 'foo': 'bar'},
        _data=external_data,
    )
    assert data.existing['stuff'] == 'more things'
    assert data.existing['foo'] == 'bar'
    assert data.public == {}
