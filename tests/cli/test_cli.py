"""Collection of tests around cookiecutter's command-line interface."""

import os
import sys

import pytest

FAKE_REPO = 'fake-repo-pre'


@pytest.fixture
def make_fake_project_dir(request):
    """Create a fake project to be overwritten in the according tests."""
    if not os.path.isdir('fake-project'):
        os.makedirs('fake-project')


@pytest.fixture(params=['-V', '--version'])
def version_cli_flag(request):
    """Pytest fixture return both version invocation options."""
    return request.param


def test_cli_version(cli_runner, version_cli_flag):
    """Verify correct version output by `cookiecutter` on cli invocation."""
    result = cli_runner(version_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith('Tackle')


def test_cli_error_on_existing_output_directory(
        change_dir_main_fixtures, cli_runner, remove_fake_project_dir
):
    """Test cli invocation without `overwrite-if-exists` fail if dir exist."""
    if not os.path.isdir('fake-project'):
        os.makedirs('fake-project')

    result = cli_runner('fake-repo-pre', '--no-input')
    # x = result.stderr

    assert result
    assert result.exit_code != 0
    assert result.output == 'Error: "fake-project" directory already exists\n'


def test_cli(cli_runner, change_dir_main_fixtures, remove_fake_project_dir):
    """Test cli invocation work without flags if directory not exist."""
    result = cli_runner('fake-repo-pre', '--no-input')
    # assert result.output
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')
    with open(os.path.join('fake-project', 'README.rst')) as f:
        assert 'Project name: **Fake Project**' in f.read()


def test_cli_verbose(change_dir_main_fixtures, remove_fake_project_dir, cli_runner):
    """Test cli invocation display log if called with `verbose` flag."""
    result = cli_runner('fake-repo-pre', '--no-input', '-v')
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')
    with open(os.path.join('fake-project', 'README.rst')) as f:
        assert 'Project name: **Fake Project**' in f.read()


# @pytest.fixture
# def fake_project_replay_dir(request):
#     s = Settings()
#     if not os.path.isdir(s.replay_dir):
#         os.mkdir(s.replay_dir)
#     yield
#     if os.path.isdir(s.replay_dir):
#         os.rmdir(s.replay_dir)
#
#
# def test_cli_replay(change_dir_main_fixtures, remove_fake_project_dir, cli_runner):
#     """Test cli invocation display log with `verbose` and `replay` flags."""
#     result = cli_runner('fake-repo-pre/', '--replay', '-v')
#
#     assert result.exit_code == 0


# TODO: Fix with replay update
# @pytest.mark.usefixtures('remove_fake_project_dir')
# def test_cli_replay_file(change_dir_main_fixtures, remove_fake_project_dir, cli_runner):
#     """Test cli invocation correctly pass --replay-file option."""
#     result = cli_runner(FAKE_REPO, '--replay-file', '~/custom-replay-file', '-v')
#
#     assert result.exit_code == 0


# @pytest.fixture(params=['-f', '--overwrite-if-exists'])
# def overwrite_cli_flag(request):
#     """Pytest fixture return all `overwrite-if-exists` invocation options."""
#     return request.param


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_overwrite_if_exists_when_output_dir_does_not_exist(
        cli_runner, overwrite_cli_flag, change_dir_main_fixtures
):
    """Test cli invocation with `overwrite-if-exists` and `no-input` flags.

    Case when output dir not exist.
    """
    result = cli_runner('fake-repo-pre', '--no-input', overwrite_cli_flag)

    assert result.exit_code == 0
    assert os.path.isdir('fake-project')


def test_cli_overwrite_if_exists_when_output_dir_exists(
        cli_runner, remove_fake_project_dir, overwrite_cli_flag, change_dir_main_fixtures
):
    """Test cli invocation with `overwrite-if-exists` and `no-input` flags.

    Case when output dir already exist.
    """
    if not os.path.isdir('fake-project'):
        os.makedirs('fake-project')

    result = cli_runner('fake-repo-pre/', '--no-input', overwrite_cli_flag)
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')


@pytest.fixture(params=['-h', '--help', 'help'])
def help_cli_flag(request):
    """Pytest fixture return all help invocation options."""
    return request.param


def test_cli_help(cli_runner, help_cli_flag):
    """Test cli invocation display help message with `help` flag."""
    result = cli_runner(help_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith('Usage')


@pytest.fixture
def user_config_path(tmpdir):
    """Pytest fixture return `user_config` argument as string."""
    return str(tmpdir.join('tests/config.yaml'))


@pytest.mark.skipif(
    sys.version_info[0] == 3 and sys.version_info[1] == 6 and sys.version_info[2] == 1,
    reason="Outdated pypy3 version on Travis CI/CD with wrong OrderedDict syntax.",
)
def test_echo_undefined_variable_error(
        monkeypatch, tmpdir, cli_runner, change_dir_main_fixtures
):
    """Cli invocation return error if variable undefined in template."""
    output_dir = str(tmpdir.mkdir('output'))
    template_path = 'undefined-variable/file-name'

    result = cli_runner(
        '--no-input', '--default-config', '--output-dir', output_dir, template_path
    )

    assert result.exit_code == 1

    error = "Unable to create file '{{cookiecutter.foobar}}'"
    assert error in result.output

    message = (
        "Error message: 'collections.OrderedDict object' has no attribute 'foobar'"
    )
    assert message in result.output


def test_echo_unknown_extension_error(tmpdir, cli_runner, change_dir_main_fixtures):
    """Cli return error if extension incorrectly defined in template."""
    output_dir = str(tmpdir.mkdir('output'))
    template_path = 'test-extensions/unknown/'

    result = cli_runner(
        '--no-input', '--default-config', '--output-dir', output_dir, template_path
    )

    assert result.exit_code == 1

    assert 'Unable to load extension: ' in result.output


def test_cli_extra_context(
        cli_runner, change_dir_main_fixtures, remove_fake_project_dir
):
    """Cli invocation replace content if called with replacement pairs."""
    result = cli_runner(
        'fake-repo-pre/',
        '--no-input',
        '-v',
        '--overwrite-inputs',
        'project_name=Awesomez',
    )
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')
    with open(os.path.join('fake-project', 'README.rst')) as f:
        assert 'Project name: **Awesomez**' in f.read()


def test_cli_extra_contexts(
        cli_runner, change_dir_main_fixtures, remove_fake_project_dir
):
    """Cli invocation replace content if called with replacement pairs."""
    result = cli_runner(
        'fake-repo-pre/',
        '--no-input',
        '-v',
        '--overwrite-inputs',
        'project_name=Awesomez stuff=things',
    )
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')
    with open(os.path.join('fake-project', 'README.rst')) as f:
        assert 'Project name: **Awesomez**' in f.read()


# TODO: Remove when finalize mode
# This is no longer valid as string input is now pointer to file
# def test_cli_extra_context_invalid_format(
#     cli_runner, change_dir_main_fixtures, remove_fake_project_dir
# ):
#     """Cli invocation raise error if called with unknown argument."""
#     result = cli_runner(
#         'fake-repo-pre/',
#         '--no-input',
#         '-v',
#         '--overwrite-inputs',
#         'ExtraContextWithNoEqualsSoInvalid',
#     )
#     assert result.exit_code == 2
#     assert "Error: Invalid value for" in result.output
#     assert 'should contain items of the form key=value' in result.output

def test_cli_overwrite_context_invalid_path(
        cli_runner, change_dir_main_fixtures, remove_fake_project_dir
):
    """Cli invocation raise error if called with unknown path argument."""
    result = cli_runner(
        'fake-repo-pre/',
        '--no-input',
        '-v',
        '--overwrite-inputs',
        'AnInvalidPathToFile',
    )
    assert FileNotFoundError in result.exc_info


def test_cli_overwrite_context_valid_path(
        cli_runner, change_dir_main_fixtures, remove_fake_project_dir
):
    """Cli invocation with path arg to overwrite_context."""
    result = cli_runner(
        'fake-repo-pre/',
        '--no-input',
        '-v',
        '--overwrite-inputs',
        os.path.join('extra-contexts', 'fake-repo-pre.yaml'),
    )
    assert result.exit_code == 0
    with open(os.path.join('fake-project', 'README.rst')) as f:
        out = f.read()
    assert 'big_stuff' in out  # This is in the overwrite context


@pytest.fixture
def debug_file(tmpdir):
    """Pytest fixture return `debug_file` argument as path object."""
    return tmpdir.join('fake-repo.log')


def test_debug_file_non_verbose(
        cli_runner, debug_file, change_dir_main_fixtures, remove_fake_project_dir
):
    """Test cli invocation writes log to `debug-file` if flag enabled.

    Case for normal log output.
    """
    assert not debug_file.exists()

    result = cli_runner('--no-input', '--debug-file', str(debug_file), 'fake-repo-pre/')
    assert result.exit_code == 0

    assert debug_file.exists()
    assert len(debug_file.readlines(cr=False)) > 10


def test_debug_file_verbose(
        cli_runner, debug_file, change_dir_main_fixtures, remove_fake_project_dir
):
    """Test cli invocation writes log to `debug-file` if flag enabled.

    Case for verbose log output.
    """
    assert not debug_file.exists()

    result = cli_runner(
        '--verbose', '--no-input', '--debug-file', str(debug_file), 'fake-repo-pre'
    )
    assert result.exit_code == 0

    assert debug_file.exists()
    assert len(debug_file.readlines(cr=False)) > 10


# TODO: Fix with update to cache
# def test_debug_list_installed_templates(
#     cli_runner,
#     debug_file,
#     user_config_path,
#     change_dir_main_fixtures,
#     make_fake_project_dir,
# ):
#     """Verify --list-installed command correct invocation."""
#     fake_template_dir = os.path.dirname(os.path.abspath('fake-project'))
#     os.makedirs(os.path.dirname(user_config_path))
#
#     with open(user_config_path, 'w') as config_file:
#         config_file.write('tackle_dir: "%s"' % fake_template_dir)
#     open(os.path.join('fake-project', 'cookiecutter.json'), 'w').write('{}')
#
#     result = cli_runner(
#         '--list-installed', '--config-file', user_config_path, str(debug_file),
#     )
#
#     assert "1 installed templates:" in result.output
#     assert result.exit_code == 0


# def test_debug_list_installed_templates_failure(
#     cli_runner, debug_file, user_config_path
# ):
#     """Verify --list-installed command error on invocation."""
#     os.makedirs(os.path.dirname(user_config_path))
#     with open(user_config_path, 'w') as config_file:
#         config_file.write('cookiecutters_dir: "/notarealplace/"')
#
#     result = cli_runner(
#         '--list-installed', '--config-file', user_config_path, str(debug_file)
#     )
#
#     assert "Error: Cannot list installed templates." in result.output
#     assert result.exit_code == -1


def test_directory_repo(cli_runner, change_dir_main_fixtures, remove_fake_project_dir):
    """Test cli invocation works with `directory` option."""
    result = cli_runner('fake-repo-dir/', '--no-input', '-v', '--directory=my-dir')
    assert result.exit_code == 0
    assert os.path.isdir("fake-project")
    with open(os.path.join("fake-project", "README.rst")) as f:
        assert "Project name: **Fake Project**" in f.read()
