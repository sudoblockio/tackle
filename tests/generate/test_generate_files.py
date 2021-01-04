"""Tests for `generate_files` function and related errors raising.

Use the global clean_system fixture and run additional teardown code to remove
some special folders.
"""
import os
from pathlib import Path

import pytest
from binaryornot.check import is_binary

import tackle.utils.paths
from tackle import exceptions
from tackle import generate
from tackle.main import tackle
from tackle.models import Source, Context, Output
from _collections import OrderedDict


@pytest.mark.parametrize('invalid_dirname', ['', '{foo}', '{{foo', 'bar}}'])
def test_ensure_dir_is_templated_raises(invalid_dirname):
    """Verify `ensure_dir_is_templated` raises on wrong directories names input."""
    with pytest.raises(exceptions.NonTemplatedInputDirException):
        generate.ensure_dir_is_templated(invalid_dirname)


@pytest.fixture(scope='function')
def remove_additional_folders():
    """Remove some special folders which are created by the tests."""
    yield
    if os.path.exists('inputpizzä'):
        tackle.utils.paths.rmtree('inputpizzä')
    if os.path.exists('inputgreen'):
        tackle.utils.paths.rmtree('inputgreen')
    if os.path.exists('inputbinary_files'):
        tackle.utils.paths.rmtree('inputbinary_files')
    if os.path.exists('tests/custom_output_dir'):
        tackle.utils.paths.rmtree('tests/custom_output_dir')
    if os.path.exists('inputpermissions'):
        tackle.utils.paths.rmtree('inputpermissions')


# Removed because now we don't want to force actual rendering now that we have more
# to do...
# @pytest.mark.usefixtures('clean_system', 'remove_additional_folders')
# def test_generate_files_nontemplated_exception():
#     """
#     Verify `generate_files` raises when no directories to render exist.
#
# Note: Check `tests/generate/test-generate-files-nontemplated` location to understand.
#     """
#     with pytest.raises(exceptions.NonTemplatedInputDirException):
#         generate.generate_files(
#             context={'cookiecutter': {'food': 'pizza'}},
#             repo_dir='tests/generate/test-generate-files-nontemplated',
#         )
# def test_generate_files_nontemplated_exception(tmp_path):
#     """
#     Verify `generate_files` raises when no directories to render exist.
#
# Note: Check `tests/generate/test-generate-files-nontemplated` location to understand.
#     """
#     with pytest.raises(exceptions.NonTemplatedInputDirException):
#         generate.generate_files(
#             context={'cookiecutter': {'food': 'pizza'}},
#             repo_dir='tests/generate/test-generate-files-nontemplated',
#             output_dir=tmp_path,
#         )


def generate_files_from_context(
    context,
    path,
    overwrite_if_exists=False,
    skip_if_file_exists=False,
    repo_dir='test-generate-files',
):
    """Generate files given a context to path."""
    c = Context(
        context_key='cookiecutter',
        input_dict=OrderedDict({'cookiecutter': context}),
        output_dict=OrderedDict(context),
        tackle_gen='cookiecutter',
    )
    s = Source(repo_dir=repo_dir)
    o = Output(
        output_dir=str(path),
        overwrite_if_exists=overwrite_if_exists,
        skip_if_file_exists=skip_if_file_exists,
    )
    output = generate.generate_files(context=c, source=s, output=o)
    return output


def test_generate_files(tmp_path, change_dir):
    """Verify directory name correctly rendered with unicode containing context."""
    context = {'food': 'pizzä'}
    generate_files_from_context(context, tmp_path)
    simple_file = Path(tmp_path, 'inputpizzä/simple.txt')
    assert simple_file.exists()
    assert simple_file.is_file()

    simple_text = open(simple_file, 'rt', encoding='utf-8').read()
    assert simple_text == 'I eat pizzä'


def test_generate_files_with_linux_newline(tmp_path, change_dir):
    """Verify new line not removed by templating engine after folder generation."""
    context = {'food': 'pizzä'}
    generate_files_from_context(context, tmp_path)

    newline_file = Path(tmp_path, 'inputpizzä/simple-with-newline.txt')
    assert newline_file.is_file()
    assert newline_file.exists()

    with open(newline_file, 'r', encoding='utf-8', newline='') as f:
        simple_text = f.readline()
    assert simple_text == 'newline is LF\n'
    assert f.newlines == '\n'


def test_generate_files_with_jinja2_environment(tmp_path, change_dir):
    """Extend StrictEnvironment with _jinja2_env_vars cookiecutter template option."""
    context = {
        'food': 'pizzä',
        '_jinja2_env_vars': {'lstrip_blocks': True, 'trim_blocks': True},
    }
    generate_files_from_context(context, tmp_path)

    conditions_file = tmp_path.joinpath('inputpizzä/simple-with-conditions.txt')
    assert conditions_file.is_file()
    assert conditions_file.exists()

    simple_text = conditions_file.open('rt', encoding='utf-8').read()
    assert simple_text == u'I eat pizzä\n'


def test_generate_files_with_trailing_newline_forced_to_linux_by_context(
    tmp_path, change_dir
):
    """Verify new line not removed by templating engine after folder generation."""
    context = {'food': 'pizzä', '_new_lines': '\r\n'}
    generate_files_from_context(context, tmp_path)

    # assert 'Overwritting endline character with %s' in caplog.messages
    newline_file = Path(tmp_path, 'inputpizzä/simple-with-newline.txt')
    assert newline_file.is_file()
    assert newline_file.exists()

    with open(newline_file, 'r', encoding='utf-8', newline='') as f:
        simple_text = f.readline()
    assert simple_text == 'newline is LF\r\n'
    assert f.newlines == '\r\n'


def test_generate_files_with_windows_newline(tmp_path):
    """Verify windows source line end not changed during files generation."""
    context = {'food': 'pizzä'}
    generate_files_from_context(context, tmp_path)

    newline_file = Path(tmp_path, 'inputpizzä/simple-with-newline-crlf.txt')
    assert newline_file.is_file()
    assert newline_file.exists()

    with open(newline_file, 'r', encoding='utf-8', newline='') as f:
        simple_text = f.readline()
    assert simple_text == 'newline is CRLF\r\n'
    assert f.newlines == '\r\n'


def test_generate_files_with_windows_newline_forced_to_linux_by_context(tmp_path):
    """Verify windows line end changed to linux during files generation."""
    context = {'food': 'pizzä', '_new_lines': '\n'}
    generate_files_from_context(context, tmp_path)

    newline_file = Path(tmp_path, 'inputpizzä/simple-with-newline-crlf.txt')
    assert newline_file.is_file()
    assert newline_file.exists()

    with open(newline_file, 'r', encoding='utf-8', newline='') as f:
        simple_text = f.readline()

    assert simple_text == 'newline is CRLF\n'
    assert f.newlines == '\n'


def test_generate_files_binaries(tmp_path):
    """Verify binary files created during directory generation."""
    context = {'binary_test': 'binary_files'}
    generate_files_from_context(context, tmp_path, repo_dir='test-generate-binaries')

    dst_dir = Path(tmp_path, 'inputbinary_files')

    assert is_binary(str(Path(dst_dir, 'logo.png')))
    assert is_binary(str(Path(dst_dir, '.DS_Store')))
    assert not is_binary(str(Path(dst_dir, 'readme.txt')))
    assert is_binary(str(Path(dst_dir, 'some_font.otf')))
    assert is_binary(str(Path(dst_dir, 'binary_files/logo.png')))
    assert is_binary(str(Path(dst_dir, 'binary_files/.DS_Store')))
    assert not is_binary(str(Path(dst_dir, 'binary_files/readme.txt')))
    assert is_binary(str(Path(dst_dir, 'binary_files/some_font.otf')))
    assert is_binary(str(Path(dst_dir, 'binary_files/binary_files/logo.png')))


def test_generate_files_absolute_path(change_dir, tmp_path):
    """Verify usage of absolute path does not change files generation behaviour."""
    context = {'food': 'pizzä'}
    generate_files_from_context(context, tmp_path, repo_dir='test-generate-files')
    assert Path(tmp_path, u'inputpizzä/simple.txt').is_file()


def test_generate_files_output_dir(monkeypatch, tmp_path):
    """Verify `output_dir` option for `generate_files` changing location correctly."""
    monkeypatch.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__))))

    output_dir = Path(tmp_path, 'custom_output_dir')
    output_dir.mkdir()

    context = {'food': 'pizzä'}
    project_dir = generate_files_from_context(
        context, output_dir, repo_dir='test-generate-files'
    )

    assert Path(output_dir, u'inputpizzä/simple.txt').exists()
    assert Path(output_dir, u'inputpizzä/simple.txt').is_file()
    assert Path(project_dir) == Path(tmp_path, u'custom_output_dir/inputpizzä')


def test_generate_files_permissions(tmp_path, change_dir):
    """Verify generates files respect source files permissions.

    simple.txt and script.sh should retain their respective 0o644 and 0o755
    permissions.
    """
    context = {'permissions': 'permissions'}
    generate_files_from_context(
        context, tmp_path, repo_dir='test-generate-files-permissions'
    )

    assert Path(tmp_path, 'inputpermissions/simple.txt').exists()
    assert Path(tmp_path, 'inputpermissions/simple.txt').is_file()

    # Verify source simple.txt should still be 0o644
    tests_simple_file = Path(
        'test-generate-files-permissions',
        'input{{cookiecutter.permissions}}',
        'simple.txt',
    )
    tests_simple_file_mode = tests_simple_file.stat().st_mode

    input_simple_file = Path(tmp_path, 'inputpermissions', 'simple.txt')
    input_simple_file_mode = input_simple_file.stat().st_mode
    assert tests_simple_file_mode == input_simple_file_mode

    assert Path(tmp_path, 'inputpermissions/script.sh').exists()
    assert Path(tmp_path, 'inputpermissions/script.sh').is_file()

    # Verify source script.sh should still be 0o755
    tests_script_file = Path(
        'test-generate-files-permissions',
        'input{{cookiecutter.permissions}}',
        'script.sh',
    )
    tests_script_file_mode = tests_script_file.stat().st_mode

    input_script_file = Path(tmp_path, 'inputpermissions', 'script.sh')
    input_script_file_mode = input_script_file.stat().st_mode
    assert tests_script_file_mode == input_script_file_mode


def test_generate_files_with_overwrite_if_exists_with_skip_if_file_exists(tmp_path):
    """Verify `skip_if_file_exist` has priority over `overwrite_if_exists`."""
    simple_file = Path(tmp_path, 'inputpizzä/simple.txt')
    simple_with_new_line_file = Path(tmp_path, 'inputpizzä/simple-with-newline.txt')

    Path(tmp_path, 'inputpizzä').mkdir(parents=True)
    with open(simple_file, 'w') as f:
        f.write('temp')
    context = {'food': 'pizzä'}
    generate_files_from_context(
        context,
        tmp_path,
        overwrite_if_exists=True,
        skip_if_file_exists=True,
        repo_dir='test-generate-files',
    )

    assert Path(simple_file).is_file()
    assert Path(simple_file).exists()
    assert Path(simple_with_new_line_file).is_file()
    assert Path(simple_with_new_line_file).exists()

    simple_text = open(simple_file, 'rt', encoding='utf-8').read()
    assert simple_text == 'temp'


def test_generate_files_with_skip_if_file_exists(tmp_path):
    """Verify existed files not removed if error raised with `skip_if_file_exists`."""
    simple_file = Path(tmp_path, 'inputpizzä/simple.txt')
    simple_with_new_line_file = Path(tmp_path, 'inputpizzä/simple-with-newline.txt')

    Path(tmp_path, 'inputpizzä').mkdir(parents=True)
    with open(simple_file, 'w') as f:
        f.write('temp')
    context = {'food': 'pizzä'}

    with pytest.raises(exceptions.OutputDirExistsException):
        generate_files_from_context(
            context, tmp_path, skip_if_file_exists=True, repo_dir='test-generate-files'
        )

    assert Path(simple_file).is_file()
    assert Path(simple_file).exists()
    assert not Path(simple_with_new_line_file).is_file()
    assert not Path(simple_with_new_line_file).exists()

    simple_text = open(simple_file, 'rt', encoding='utf-8').read()
    assert simple_text == 'temp'


def test_generate_files_with_overwrite_if_exists(tmp_path):
    """Verify overwrite_if_exists overwrites old files."""
    simple_file = Path(tmp_path, 'inputpizzä/simple.txt')
    simple_with_new_line_file = Path(tmp_path, 'inputpizzä/simple-with-newline.txt')

    Path(tmp_path, 'inputpizzä').mkdir(parents=True)
    with open(simple_file, 'w') as f:
        f.write('temp')
    context = {'food': 'pizzä'}

    generate_files_from_context(
        context, tmp_path, overwrite_if_exists=True, repo_dir='test-generate-files'
    )

    assert Path(simple_file).is_file()
    assert Path(simple_file).exists()
    assert Path(simple_with_new_line_file).is_file()
    assert Path(simple_with_new_line_file).exists()

    simple_text = open(simple_file, 'rt', encoding='utf-8').read()
    assert simple_text == 'I eat pizzä'


@pytest.fixture
def undefined_context():
    """Fixture. Populate context variable for future tests."""
    return {
        'cookiecutter': {'project_slug': 'testproject', 'github_username': 'hackebrot'}
    }


def test_raise_undefined_variable_file_name(
    tmpdir, undefined_context, change_dir_main_fixtures
):
    """Verify correct error raised when file name cannot be rendered."""
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        tackle(
            'undefined-variable/file-name',
            no_input=True,
            output_dir=str(output_dir),
            existing_context=undefined_context,
        )

    error = err.value
    assert "Unable to create file '{{cookiecutter.foobar}}'" == error.message
    assert not output_dir.join('testproject').exists()


def test_raise_undefined_variable_file_name_existing_project(
    tmpdir, undefined_context, change_dir_main_fixtures
):
    """Verify correct error raised when file name cannot be rendered."""
    output_dir = tmpdir.mkdir('output')

    output_dir.join('testproject').mkdir()

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        tackle(
            'undefined-variable/file-name',
            no_input=True,
            output_dir=str(output_dir),
            existing_context=undefined_context,
            overwrite_if_exists=True,
        )

    error = err.value
    assert "Unable to create file '{{cookiecutter.foobar}}'" == error.message
    del error.context['cookiecutter']['_template']
    assert error.context == undefined_context
    assert output_dir.join('testproject').exists()


def test_raise_undefined_variable_file_content(
    tmpdir, undefined_context, change_dir_main_fixtures
):
    """Verify correct error raised when file content cannot be rendered."""
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        tackle(
            'undefined-variable/file-content',
            no_input=True,
            output_dir=str(output_dir),
            existing_context=undefined_context,
        )

    error = err.value
    assert "Unable to create file 'README.rst'" == error.message
    del error.context['cookiecutter']['_template']
    assert error.context == undefined_context

    assert not output_dir.join('testproject').exists()


def test_raise_undefined_variable_dir_name(
    tmpdir, undefined_context, change_dir_main_fixtures
):
    """Verify correct error raised when directory name cannot be rendered."""
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        tackle(
            'undefined-variable/dir-name',
            no_input=True,
            output_dir=str(output_dir),
            existing_context={'project_slug': 'testproject'},
        )

    error = err.value

    directory = os.path.join('testproject', '{{cookiecutter.foobar}}')
    msg = "Unable to create directory '{}'".format(directory)
    assert msg == error.message

    assert not output_dir.join('testproject').exists()


def test_raise_undefined_variable_dir_name_existing_project(
    tmpdir, undefined_context, change_dir_main_fixtures
):
    """Verify correct error raised when directory name cannot be rendered."""
    output_dir = tmpdir.mkdir('output')

    output_dir.join('testproject').mkdir()

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        tackle(
            'undefined-variable/dir-name',
            no_input=True,
            output_dir=str(output_dir),
            overwrite_if_exists=True,
            existing_context={'project_slug': 'testproject'},
        )
    error = err.value

    directory = os.path.join('testproject', '{{cookiecutter.foobar}}')
    msg = "Unable to create directory '{}'".format(directory)
    assert msg == error.message

    assert output_dir.join('testproject').exists()


def test_raise_undefined_variable_project_dir(tmpdir, change_dir_main_fixtures):
    """Verify correct error raised when directory name cannot be rendered."""
    output_dir = tmpdir.mkdir('output')

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        tackle(
            'undefined-variable/dir-name', no_input=True, output_dir=str(output_dir),
        )

    error = err.value
    msg = "Unable to create project directory '{{cookiecutter.project_slug}}'"
    assert msg == error.message
