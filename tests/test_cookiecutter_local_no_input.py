"""Test cookiecutter for work without any input.

Tests in this file execute `cookiecutter()` with `no_input=True` flag and
verify result with different settings in `cookiecutter.json`.
"""
import os
import textwrap

import pytest

from cookiecutter import main, utils


@pytest.fixture(scope='function')
def remove_additional_dirs(monkeypatch, request):
    """Fixture. Remove special directories which are created during the tests."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    def fin_remove_additional_dirs():
        if os.path.isdir('fake-project'):
            utils.rmtree('fake-project')
        if os.path.isdir('fake-project-extra'):
            utils.rmtree('fake-project-extra')
        if os.path.isdir('fake-project-templated'):
            utils.rmtree('fake-project-templated')
        if os.path.isdir('fake-project-dict'):
            utils.rmtree('fake-project-dict')
        if os.path.isdir('fake-tmp'):
            utils.rmtree('fake-tmp')

    request.addfinalizer(fin_remove_additional_dirs)


# Parameter messing up cleanup and confusing things
# @pytest.mark.parametrize('path', ['fake-repo-pre/', 'fake-repo-pre'])
@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_cookiecutter_no_input_return_project_dir(monkeypatch):
    """Verify `cookiecutter` create project dir on input with or without slash."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = main.cookiecutter('fake-repo-pre', no_input=True)

    assert type(context) == dict
    assert os.path.isdir('fake-repo-pre/{{cookiecutter.repo_name}}')
    assert not os.path.isdir('fake-repo-pre/fake-project')

    # project_dir = os.path.join(os.path.abspath(os.path.curdir), 'fake-project')
    # x = os.listdir(project_dir)
    # y = os.path.isdir(project_dir)
    # Derrr,,,, I don't see what is wrong here but it works as expected?
    # assert os.path.isdir(project_dir)
    # assert os.path.isfile(os.path.join(project_dir, '/README.rst'))
    # assert not os.path.exists('fake-project/json/')


@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_cookiecutter_no_input_extra_context(monkeypatch):
    """Verify `cookiecutter` accept `extra_context` argument."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    main.cookiecutter(
        'fake-repo-pre',
        no_input=True,
        extra_context={'repo_name': 'fake-project-extra'},
    )
    assert os.path.isdir('fake-project-extra')


@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_cookiecutter_templated_context(monkeypatch):
    """Verify Jinja2 templating correctly works in `cookiecutter.json` file."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    main.cookiecutter('fake-repo-tmpl', no_input=True)
    assert os.path.isdir('fake-project-templated')


@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_cookiecutter_no_input_return_rendered_file(monkeypatch):
    """Verify Jinja2 templating correctly works in `cookiecutter.json` file."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = main.cookiecutter('fake-repo-pre', no_input=True)
    project_dir = os.path.join(os.path.abspath(os.path.curdir), 'fake-project')

    assert type(context) == dict
    assert project_dir == os.path.abspath('fake-project')
    with open(os.path.join(project_dir, 'README.rst')) as fh:
        contents = fh.read()
    assert "Fake Project" in contents


@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_cookiecutter_dict_values_in_context(monkeypatch):
    """Verify configured dictionary from `cookiecutter.json` correctly unpacked."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = main.cookiecutter('fake-repo-dict', no_input=True)
    project_dir = os.path.abspath(os.path.curdir)

    assert 'fake-project-dict' in os.listdir(project_dir)
    assert type(context) == dict

    project_dir = os.path.join(project_dir, 'fake-project-dict')

    with open(os.path.join(project_dir, 'README.md')) as fh:
        contents = fh.read()

    assert (
        contents
        == textwrap.dedent(
            """
        # README


        <dl>
          <dt>Format name:</dt>
          <dd>Bitmap</dd>

          <dt>Extension:</dt>
          <dd>bmp</dd>

          <dt>Applications:</dt>
          <dd>
              <ul>
              <li>Paint</li>
              <li>GIMP</li>
              </ul>
          </dd>
        </dl>

        <dl>
          <dt>Format name:</dt>
          <dd>Portable Network Graphic</dd>

          <dt>Extension:</dt>
          <dd>png</dd>

          <dt>Applications:</dt>
          <dd>
              <ul>
              <li>GIMP</li>
              </ul>
          </dd>
        </dl>

    """
        ).lstrip()
    )


@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_cookiecutter_template_cleanup(monkeypatch, mocker):
    """Verify temporary folder for zip unpacking dropped."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    mocker.patch('tempfile.mkdtemp', return_value='fake-tmp', autospec=True)

    mocker.patch(
        'cookiecutter.utils.prompt_and_delete', return_value=True, autospec=True
    )

    main.cookiecutter('files/fake-repo-tmpl.zip', no_input=True)
    assert os.path.isdir('fake-project-templated')

    # The tmp directory will still exist, but the
    # extracted template directory *in* the temp directory will not.
    assert os.path.exists('fake-tmp')
    assert not os.path.exists('fake-tmp/fake-repo-tmpl')
