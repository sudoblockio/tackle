"""Test work of python and shell hooks for generated projects."""
import errno
import os
import sys

import pytest

from _collections import OrderedDict

from tackle.models import Context, Source, Output
import tackle.utils.paths
from tackle import generate
from tackle.exceptions import FailedHookException

WINDOWS = sys.platform.startswith('win')


def _delete_dirs(tmpdir):
    directories_to_delete = [
        'test-pyhooks/inputpyhooks',
        'inputpyhooks',
        'inputhooks',
        os.path.join(str(tmpdir), 'test-shellhooks'),
        'test-hooks',
    ]
    for directory in directories_to_delete:
        if os.path.exists(directory):
            tackle.utils.paths.rmtree(directory)
    if os.path.exists('shell_post.txt'):
        os.remove('shell_post.txt')


@pytest.fixture(scope='function')
def remove_additional_folders(tmpdir, change_dir_main_fixtures):
    """Remove some special folders which are created by the tests."""
    _delete_dirs(tmpdir)
    yield
    _delete_dirs(tmpdir)


def generate_files_wrapper(
    repo_dir,
    context=None,
    output_dir='.',
    overwrite_if_exists=False,
    skip_if_file_exists=False,
    accept_hooks=True,
):
    """Generate files given a context to path."""
    c = Context(
        context_key='cookiecutter',
        input_dict=OrderedDict(context),
        output_dict=OrderedDict(context['cookiecutter']),
        tackle_gen='cookiecutter',
    )
    s = Source(repo_dir=repo_dir)
    o = Output(
        output_dir=str(output_dir),
        overwrite_if_exists=overwrite_if_exists,
        skip_if_file_exists=skip_if_file_exists,
        accept_hooks=accept_hooks,
    )
    output = generate.generate_files(context=c, source=s, output=o)
    return output


@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_ignore_hooks_dirs(change_dir_main_fixtures):
    """Verify hooks directory not created in target location on files generation."""
    generate_files_wrapper(
        context={'cookiecutter': {'pyhooks': 'pyhooks'}},
        repo_dir='test-pyhooks/',
        output_dir='test-pyhooks/',
    )
    assert not os.path.exists('test-pyhooks/inputpyhooks/hooks')


@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_run_python_hooks(change_dir_main_fixtures):
    """Verify pre and post generation python hooks executed and result in output_dir.

    Each hook should create in target directory. Test verifies that these files
    created.
    """
    generate_files_wrapper(
        context={'cookiecutter': {'pyhooks': 'pyhooks'}},
        repo_dir='test-pyhooks/',
        output_dir='test-pyhooks/',
    )
    assert os.path.exists('test-pyhooks/inputpyhooks/python_pre.txt')
    assert os.path.exists('test-pyhooks/inputpyhooks/python_post.txt')


@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_run_python_hooks_cwd():
    """Verify pre and post generation python hooks executed and result in current dir.

    Each hook should create in target directory. Test verifies that these files
    created.
    """
    generate_files_wrapper(
        context={'cookiecutter': {'pyhooks': 'pyhooks'}}, repo_dir='test-pyhooks/',
    )
    assert os.path.exists('inputpyhooks/python_pre.txt')
    assert os.path.exists('inputpyhooks/python_post.txt')


@pytest.mark.skipif(WINDOWS, reason='OSError.errno=8 is not thrown on Windows')
@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_empty_hooks():
    """Verify error is raised on empty hook script. Ignored on windows.

    OSError.errno=8 is not thrown on Windows when the script is empty
    because it always runs through shell instead of needing a shebang.
    """
    with pytest.raises(FailedHookException) as excinfo:
        generate_files_wrapper(
            context={'cookiecutter': {'shellhooks': 'shellhooks'}},
            repo_dir='test-shellhooks-empty/',
            overwrite_if_exists=True,
        )
    assert 'shebang' in str(excinfo.value)


@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_oserror_hooks(mocker):
    """Verify script error passed correctly to cookiecutter error.

    Here subprocess.Popen function mocked, ie we do not call hook script,
    just produce expected error.
    """
    message = 'Out of memory'

    err = OSError(message)
    err.errno = errno.ENOMEM

    prompt = mocker.patch('subprocess.Popen')
    prompt.side_effect = err

    with pytest.raises(FailedHookException) as excinfo:
        generate_files_wrapper(
            context={'cookiecutter': {'shellhooks': 'shellhooks'}},
            repo_dir='test-shellhooks-empty/',
            overwrite_if_exists=True,
        )
    assert message in str(excinfo.value)


@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_run_failing_hook_removes_output_directory():
    """Verify project directory not created or removed if hook failed."""
    repo_path = os.path.abspath('test-hooks/')
    hooks_path = os.path.abspath('test-hooks/hooks')

    hook_dir = os.path.join(repo_path, 'hooks')
    template = os.path.join(repo_path, 'input{{cookiecutter.hooks}}')
    os.mkdir(repo_path)
    os.mkdir(hook_dir)
    os.mkdir(template)

    hook_path = os.path.join(hooks_path, 'pre_gen_project.py')

    with open(hook_path, 'w') as f:
        f.write("#!/usr/bin/env python\n")
        f.write("import sys; sys.exit(1)\n")

    with pytest.raises(FailedHookException) as excinfo:
        generate_files_wrapper(
            context={'cookiecutter': {'hooks': 'hooks'}},
            repo_dir='test-hooks/',
            overwrite_if_exists=True,
        )

    assert 'Hook script failed' in str(excinfo.value)
    assert not os.path.exists('inputhooks')


@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_run_failing_hook_preserves_existing_output_directory():
    """Verify project directory not removed if exist before hook failed."""
    repo_path = os.path.abspath('test-hooks/')
    hooks_path = os.path.abspath('test-hooks/hooks')

    hook_dir = os.path.join(repo_path, 'hooks')
    template = os.path.join(repo_path, 'input{{cookiecutter.hooks}}')
    os.mkdir(repo_path)
    os.mkdir(hook_dir)
    os.mkdir(template)

    hook_path = os.path.join(hooks_path, 'pre_gen_project.py')

    with open(hook_path, 'w') as f:
        f.write("#!/usr/bin/env python\n")
        f.write("import sys; sys.exit(1)\n")

    os.mkdir('inputhooks')
    with pytest.raises(FailedHookException) as excinfo:
        generate_files_wrapper(
            context={'cookiecutter': {'hooks': 'hooks'}},
            repo_dir='test-hooks/',
            overwrite_if_exists=True,
        )

    assert 'Hook script failed' in str(excinfo.value)
    assert os.path.exists('inputhooks')


@pytest.mark.skipif(sys.platform.startswith('win'), reason="Linux only test")
@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_run_shell_hooks(tmpdir):
    """Verify pre and post generate project shell hooks executed.

    This test for .sh files.
    """
    generate_files_wrapper(
        context={'cookiecutter': {'shellhooks': 'shellhooks'}},
        repo_dir='test-shellhooks/',
        output_dir=os.path.join(str(tmpdir), 'test-shellhooks'),
    )
    shell_pre_file = os.path.join(
        str(tmpdir), 'test-shellhooks', 'inputshellhooks', 'shell_pre.txt'
    )
    shell_post_file = os.path.join(
        str(tmpdir), 'test-shellhooks', 'inputshellhooks', 'shell_post.txt'
    )
    assert os.path.exists(shell_pre_file)
    assert os.path.exists(shell_post_file)


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="Win only test")
@pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
def test_run_shell_hooks_win(tmpdir):
    """Verify pre and post generate project shell hooks executed.

    This test for .bat files.
    """
    generate_files_wrapper(
        context={'cookiecutter': {'shellhooks': 'shellhooks'}},
        repo_dir='test-shellhooks-win/',
        output_dir=os.path.join(str(tmpdir), 'test-shellhooks-win'),
    )
    shell_pre_file = os.path.join(
        str(tmpdir), 'test-shellhooks-win', 'inputshellhooks', 'shell_pre.txt'
    )
    shell_post_file = os.path.join(
        str(tmpdir), 'test-shellhooks-win', 'inputshellhooks', 'shell_post.txt'
    )
    assert os.path.exists(shell_pre_file)
    assert os.path.exists(shell_post_file)


@pytest.mark.usefixtures("clean_system", "remove_additional_folders")
def test_ignore_shell_hooks(tmp_path):
    """Verify *.txt files not created, when accept_hooks=False."""
    generate_files_wrapper(
        context={"cookiecutter": {"shellhooks": "shellhooks"}},
        repo_dir="test-shellhooks/",
        output_dir=tmp_path.joinpath('test-shellhooks'),
        accept_hooks=False,
    )
    shell_pre_file = tmp_path.joinpath("test-shellhooks/inputshellhooks/shell_pre.txt")
    shell_post_file = tmp_path.joinpath(
        "test-shellhooks/inputshellhooks/shell_post.txt"
    )
    assert not shell_pre_file.exists()
    assert not shell_post_file.exists()
