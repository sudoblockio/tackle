"""
test_cookiecutter_invocation.

Tests to make sure that cookiecutter can be called from the cli without
using the entry point set up for the package.
"""
import os
import subprocess
import sys
from tackle.utils.paths import rmtree
import pytest

FAKE_REPO = 'fake-repo-pre'


@pytest.fixture()
def clean_output(change_dir_main_fixtures):
    if os.path.isdir('fake-project-templated'):
        rmtree('fake-project-templated')
    yield
    if os.path.isdir('fake-project-templated'):
        rmtree('fake-project-templated')


@pytest.mark.usefixtures('clean_system', 'clean_output')
def test_should_invoke_main(project_dir, change_dir_main_fixtures):
    """Should create a project and exit with 0 code on cli invocation."""
    exit_code = subprocess.check_call(
        [sys.executable, '-m', 'tackle.cli.cli_parser', 'fake-repo-tmpl', '--no-input']
    )
    assert exit_code == 0
    assert os.path.isdir(project_dir)


@pytest.fixture
def user_config_path(tmpdir):
    """Pytest fixture return `user_config` argument as string."""
    return str(tmpdir.join('tests/config.yaml'))


@pytest.fixture
def output_dir(tmpdir):
    """Pytest fixture return `output_dir` argument as string."""
    return str(tmpdir.mkdir('output'))


@pytest.fixture(params=['-o', '--output-dir'])
def output_dir_flag(request):
    """Pytest fixture return all output-dir invocation options."""
    return request.param


def test_cli_output_dir(
    mocker, cli_runner, output_dir_flag, output_dir, change_dir_main_fixtures
):
    """Test cli invocation with `output-dir` flag changes output directory."""
    mock = mocker.patch('tackle.cli.cli_parser.tackle')

    result = cli_runner(FAKE_REPO, output_dir_flag, output_dir)

    assert result.exit_code == 0
    assert mock.call_count == 1


def test_default_user_config_overwrite(
    mocker, cli_runner, user_config_path, change_dir_main_fixtures
):
    """Test cli invocation ignores `config-file` if `default-config` passed."""
    mock = mocker.patch('tackle.cli.cli_parser.tackle')

    result = cli_runner(
        FAKE_REPO, '--config-file', user_config_path, '--default-config',
    )

    assert result.exit_code == 0
    assert mock.call_count == 1
    # mock.assert_called_once_with(
    #     template_path,
    #     checkout=None,
    #     no_input=False,
    #     context_file=None,
    #     context_key=None,
    #     replay=False,
    #     overwrite_if_exists=False,
    #     skip_if_file_exists=False,
    #     output_dir='.',
    #     config_file=user_config_path,
    #     default_config=True,
    #     extra_context=None,
    #     password=None,
    #     directory=None,
    #     accept_hooks=True,
    # )


def test_user_config(mocker, cli_runner, user_config_path):
    """Test cli invocation works with `config-file` option."""
    mock = mocker.patch('tackle.cli.cli_parser.tackle')
    result = cli_runner(FAKE_REPO, '--config-file', user_config_path)

    assert result.exit_code == 0
    assert mock.call_count == 1
    # mock.assert_called_once_with(
    #     template_path,
    #     checkout=None,
    #     no_input=False,
    #     context_file=None,
    #     context_key=None,
    #     replay=False,
    #     overwrite_if_exists=False,
    #     skip_if_file_exists=False,
    #     output_dir='.',
    #     config_file=user_config_path,
    #     default_config=False,
    #     extra_context=None,
    #     password=None,
    #     directory=None,
    #     accept_hooks=True,
    # )


def test_default_user_config(mocker, cli_runner):
    """Test cli invocation accepts `default-config` flag correctly."""
    mock = mocker.patch('tackle.cli.cli_parser.tackle')
    result = cli_runner(FAKE_REPO, '--default-config')

    assert result.exit_code == 0
    assert mock.call_count == 1
    # mock.assert_called_once_with(
    #     FAKE_REPO,
    #     checkout=None,
    #     no_input=False,
    #     context_file=None,
    #     context_key=None,
    #     replay=False,
    #     overwrite_if_exists=False,
    #     skip_if_file_exists=False,
    #     output_dir='.',
    #     config_file=None,
    #     default_config=True,
    #     extra_context=None,
    #     password=None,
    #     directory=None,
    #     accept_hooks=True,
    # )


cli_accept_hook_arg_testdata = [
    ("--accept-hooks=yes", None, True),
    ("--accept-hooks=no", None, False),
    ("--accept-hooks=ask", "yes", True),
    ("--accept-hooks=ask", "no", False),
]


@pytest.mark.parametrize(
    "accept_hooks_arg,user_input,expected", cli_accept_hook_arg_testdata
)
def test_cli_accept_hooks(
    mocker,
    cli_runner,
    output_dir_flag,
    output_dir,
    accept_hooks_arg,
    user_input,
    expected,
    change_dir_main_fixtures,
):
    """Test cli invocation works with `accept-hooks` option."""
    mock = mocker.patch('tackle.cli.cli_parser.tackle')
    result = cli_runner(
        FAKE_REPO, output_dir_flag, output_dir, accept_hooks_arg, input=user_input
    )

    assert result.exit_code == 0
    assert mock.call_count == 1

    # mock.assert_called_once_with(
    #     FAKE_REPO,
    #     checkout=None,
    #     no_input=False,
    #     replay=False,
    #     context_file=None,
    #     context_key=None,
    #     overwrite_if_exists=False,
    #     output_dir=output_dir,
    #     config_file=None,
    #     default_config=False,
    #     extra_context=None,
    #     password=None,
    #     directory=None,
    #     skip_if_file_exists=False,
    #     accept_hooks=expected,
    # )


def test_run_cookiecutter_on_overwrite_if_exists_and_replay(
    mocker, cli_runner, overwrite_cli_flag, change_dir_main_fixtures
):
    """Test cli invocation with `overwrite-if-exists` and `replay` flags."""
    mock = mocker.patch('tackle.cli.cli_parser.tackle')
    result = cli_runner(FAKE_REPO, '--replay', '-v', overwrite_cli_flag)

    assert result.exit_code == 0
    assert mock.call_count == 1
    # mock.assert_called_once_with(
    #     FAKE_REPO,
    #     checkout=None,
    #     no_input=False,
    #     context_file=None,
    #     context_key=None,
    #     replay=True,
    #     overwrite_if_exists=True,
    #     skip_if_file_exists=False,
    #     output_dir='.',
    #     config_file=None,
    #     default_config=False,
    #     extra_context=None,
    #     password=None,
    #     directory=None,
    #     accept_hooks=True,
    # )


# @pytest.mark.usefixtures('remove_fake_project_dir')
# def test_cli_exit_on_noinput_and_replay(mocker, cli_runner):
#     """Test cli invocation fail if both `no-input` and `replay` flags passed."""
#     mock_cookiecutter = mocker.patch(
#         'tackle.cli.cli_parser.cookiecutter', side_effect=tackle
#     )
#
#     template_path = 'tests/legacy/fixtures/fake-repo-pre/'
#     result = cli_runner(template_path, '--no-input', '--replay', '-v')
#
#     assert result.exit_code == 1
#
#     expected_error_msg = (
#         "You can not use both replay and no_input or extra_context at the same time."
#     )
#
#     assert expected_error_msg in result.output
#
#     mock_cookiecutter.assert_called_once_with(
#         template_path,
#         checkout=None,
#         no_input=True,
#         context_file=None,
#         context_key=None,
#         replay=True,
#         overwrite_if_exists=False,
#         skip_if_file_exists=False,
#         output_dir='.',
#         config_file=None,
#         default_config=False,
#         extra_context=None,
#         password=None,
#         directory=None,
#         accept_hooks=True,
#     )
