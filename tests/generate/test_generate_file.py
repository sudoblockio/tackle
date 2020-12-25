"""Tests for `generate_file` function, part of `generate_files` function workflow."""
import json
import os
from _collections import OrderedDict

import pytest
from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError

from tackle import generate
from tackle.render.environment import StrictEnvironment
from tackle.models import Context, Output
from tackle.main import tackle
from tackle.utils.paths import rmtree


@pytest.fixture(scope='function', autouse=True)
def tear_down(change_dir_main_fixtures):
    """
    Fixture. Remove the test text file which is created by the tests.

    Used for all tests in this file.
    """
    if os.path.exists('files/cheese.txt'):
        os.remove('files/cheese.txt')
    if os.path.exists('files/cheese_lf_newlines.txt'):
        os.remove('files/cheese_lf_newlines.txt')
    if os.path.exists('files/cheese_crlf_newlines.txt'):
        os.remove('files/cheese_crlf_newlines.txt')
    yield
    if os.path.exists('files/cheese.txt'):
        os.remove('files/cheese.txt')
    if os.path.exists('files/cheese_lf_newlines.txt'):
        os.remove('files/cheese_lf_newlines.txt')
    if os.path.exists('files/cheese_crlf_newlines.txt'):
        os.remove('files/cheese_crlf_newlines.txt')


@pytest.fixture
def remove_test_dir():
    """Fixture. Remove the folder that is created by the test."""
    if os.path.exists('output_folder'):
        rmtree('output_folder')
    yield
    if os.path.exists('output_folder'):
        rmtree('output_folder')


def test_generate_file(tmpdir, change_dir, remove_test_dir):
    """Verify simple file is generated with rendered context data."""
    tackle('test-generate-files-line-end', no_input=True)

    rendered_file = os.path.join('output_folder', 'im_a.dir', 'im_a.file.py')
    assert os.path.isfile(rendered_file)
    with open(rendered_file, 'rt') as f:
        generated_text = f.read()
        assert 'This is the contents of im_a.file.py' in generated_text


def generate_file_wrapper(project_dir, infile, context, skip_if_file_exists=False):
    """Wrap the cookiecutter function call for migration of tests."""
    c = Context(
        context_key='cookiecutter',
        input_dict=OrderedDict(context),
        output_dict=OrderedDict(context['cookiecutter']),
    )
    o = Output(infile=infile, skip_if_file_exists=skip_if_file_exists,)

    envvars = c.input_dict.get(c.context_key, {}).get('_jinja2_env_vars', {})
    o.env = StrictEnvironment(
        context=c.input_dict, keep_trailing_newline=True, **envvars
    )
    o.env.loader = FileSystemLoader('.')

    output = generate.generate_file(project_dir=project_dir, context=c, output=o)
    return output


def test_generate_file_jsonify_filter(change_dir_main_fixtures, tear_down):
    """Verify jsonify filter works during files generation process."""
    infile = 'files/{{cookiecutter.jsonify_file}}.txt'
    data = {'jsonify_file': 'cheese', 'type': 'roquefort'}

    generate_file_wrapper(
        project_dir=".", infile=infile, context={'cookiecutter': data}
    )
    assert os.path.isfile('files/cheese.txt')
    with open('files/cheese.txt', 'rt') as f:
        generated_text = f.read()
        assert json.loads(generated_text) == data


@pytest.mark.parametrize("length", (10, 40))
@pytest.mark.parametrize("punctuation", (True, False))
def test_generate_file_random_ascii_string(
    length, punctuation, change_dir_main_fixtures
):
    """Verify correct work of random_ascii_string extension on file generation."""
    infile = 'files/{{cookiecutter.random_string_file}}.txt'
    # data = {'random_string_file': 'cheese'}
    data = {
        'random_string_file': 'cheese',
        "length": length,
        "punctuation": punctuation,
    }
    context = {"cookiecutter": data, "length": length, "punctuation": punctuation}
    generate_file_wrapper(project_dir=".", infile=infile, context=context)
    # generate.generate_file(project_dir=".", infile=infile, context=context, env=env)
    assert os.path.isfile('files/cheese.txt')
    with open('files/cheese.txt', 'rt') as f:
        generated_text = f.read()
        # TODO: Fix this?? - Not worth the time likely
        # When updating to tackle, had to add the +1 below
        # as it is adding a new line with this extension.
        # Also had to include punctionation and length in context
        # This extension doesn't seem very helpful when when you can
        # use a hook instead.
        assert len(generated_text) == length + 1


def test_generate_file_with_true_condition(change_dir_main_fixtures, tear_down):
    """Verify correct work of boolean condition in file name on file generation.

    This test has positive answer, so file should be rendered.
    """
    infile = 'files/{% if cookiecutter.generate_file == \'y\' %}cheese.txt{% endif %}'
    generate_file_wrapper(
        project_dir=".", infile=infile, context={'cookiecutter': {'generate_file': 'y'}}
    )
    assert os.path.isfile('files/cheese.txt')
    with open('files/cheese.txt', 'rt') as f:
        generated_text = f.read()
        assert generated_text == 'Testing that generate_file was y'


@pytest.mark.usefixtures('tear_down')
def test_generate_file_with_false_condition(change_dir_main_fixtures):
    """Verify correct work of boolean condition in file name on file generation.

    This test has negative answer, so file should not be rendered.
    """
    infile = 'files/{% if cookiecutter.generate_file == \'y\' %}cheese.txt{% endif %}'
    generate_file_wrapper(
        project_dir=".", infile=infile, context={'cookiecutter': {'generate_file': 'n'}}
    )
    assert not os.path.isfile('files/cheese.txt')


@pytest.fixture
def expected_msg(change_dir_main_fixtures):
    """Fixture. Used to ensure that exception generated text contain full data."""
    msg = (
        'Missing end of comment tag\n'
        '  File "./files/syntax_error.txt", line 1\n'
        '    I eat {{ syntax_error }} {# this comment is not closed}'
    )
    return msg.replace("/", os.sep)


def test_generate_file_verbose_template_syntax_error(
    expected_msg, change_dir_main_fixtures, tear_down
):
    """Verify correct exception raised on syntax error in file before generation."""
    with pytest.raises(TemplateSyntaxError) as exception:
        generate_file_wrapper(
            project_dir=".",
            infile='files/syntax_error.txt',
            context={'cookiecutter': {'syntax_error': 'syntax_error'}},
        )
    assert str(exception.value) == expected_msg


def test_generate_file_does_not_translate_lf_newlines_to_crlf(
    tmp_path, change_dir_main_fixtures, tear_down
):
    """Verify that file generation use same line ending, as in source file."""
    infile = 'files/{{cookiecutter.generate_file}}_lf_newlines.txt'
    generate_file_wrapper(
        project_dir=".",
        infile=infile,
        context={'cookiecutter': {'generate_file': 'cheese'}},
    )

    # this generated file should have a LF line ending
    gf = 'files/cheese_lf_newlines.txt'
    with open(gf, 'r', encoding='utf-8', newline='') as f:
        simple_text = f.readline()
    assert simple_text == 'newline is LF\n'
    assert f.newlines == '\n'


def test_generate_file_does_not_translate_crlf_newlines_to_lf(
    change_dir_main_fixtures, tear_down
):
    """Verify that file generation use same line ending, as in source file."""
    infile = 'files/{{cookiecutter.generate_file}}_crlf_newlines.txt'
    generate_file_wrapper(
        project_dir=".",
        infile=infile,
        context={'cookiecutter': {'generate_file': 'cheese'}},
    )
    # this generated file should have a CRLF line ending
    gf = 'files/cheese_crlf_newlines.txt'
    with open(gf, 'r', encoding='utf-8', newline='') as f:
        simple_text = f.readline()
    assert simple_text == 'newline is CRLF\r\n'
    assert f.newlines == '\r\n'
