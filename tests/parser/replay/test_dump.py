"""test_dump."""
import os
from tackle.utils import files


import pytest


@pytest.fixture
def template_name():
    """Fixture to return a valid template_name."""
    return 'cookiedozer'


@pytest.fixture
def replay_file(monkeypatch, replay_test_dir, template_name):
    """Fixture to return a actual file name of the dump."""
    monkeypatch.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

    file_name = '{}.json'.format(template_name)
    return os.path.join(replay_test_dir, file_name)


@pytest.fixture(autouse=True)
def remove_replay_dump(request, replay_file):
    """Remove the replay file created by tests."""

    def fin_remove_replay_file():
        if os.path.exists(replay_file):
            os.remove(replay_file)

    request.addfinalizer(fin_remove_replay_file)


# def test_type_error_if_no_template_name(replay_test_dir, context):
#     """Test that replay.dump raises if the template_name is not a valid str."""
#     with pytest.raises(TypeError):
#         files.dump(replay_test_dir, None, context)


# def test_type_error_if_not_dict_context(replay_test_dir, template_name):
#     """Test that replay.dump raises if the context is not of type dict."""
#     with pytest.raises(TypeError):
#         files.dump(replay_test_dir, template_name, 'not_a_dict')


# Deprecated due to wanting flexible context key now
# def test_value_error_if_key_missing_in_context(replay_test_dir, template_name):
#     """Test that replay.dump raises if the context does not contain a key \
#     named 'cookiecutter'."""
#     with pytest.raises(ValueError):
#         replay.dump(replay_test_dir, template_name, {'foo': 'bar'})


@pytest.fixture
def mock_ensure_failure(mocker):
    """Replace tackle.replay.make_sure_path_exists function.

    Used to mock internal function and limit test scope.
    Always return expected value: False
    """
    return mocker.patch('tackle.utils.paths.make_sure_path_exists', return_value=False)


@pytest.fixture
def mock_ensure_success(mocker):
    """Replace tackle.replay.make_sure_path_exists function.

    Used to mock internal function and limit test scope.
    Always return expected value: True
    """
    return mocker.patch('tackle.utils.paths.make_sure_path_exists', return_value=True)


# def test_ioerror_if_replay_dir_creation_fails(mock_ensure_failure, replay_test_dir, tmpdir):
#     """Test that replay.dump raises when the replay_dir cannot be created."""
#     with pytest.raises(IOError):
#         files.dump(replay_test_dir, 'foo', {'cookiecutter': {'hello': 'world'}}, str(tmpdir))
#
#     mock_ensure_failure.assert_called_once_with(replay_test_dir)


def test_run_json_dump(
    change_dir_main_fixtures,
    mocker,
    mock_ensure_success,
    mock_user_config,
    template_name,
    context,
    replay_test_dir,
    replay_file,
):
    """Test that replay.dump runs json.dump under the hood and that the context \
    is correctly written to the expected file in the replay_dir."""
    files.dump(replay_test_dir, template_name, context, replay_test_dir)
    assert not mock_user_config.called

    # spy_get_replay_file = mocker.spy(files, 'get_file_name')
    # mock_json_dump = mocker.patch('json.dump', side_effect=json.dump)
    # mock_ensure_success.assert_called_once_with(replay_test_dir)
    # spy_get_replay_file.assert_called_once_with(replay_test_dir, template_name)
    #
    # assert mock_json_dump.call_count == 1
    # (dumped_context, outfile_handler), kwargs = mock_json_dump.call_args
    # assert outfile_handler.name == replay_file
    # assert dumped_context == context
