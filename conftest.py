"""pytest fixtures which are globally available throughout the suite."""
import os
import oyaml as yaml
from click.testing import CliRunner
from tackle.__main__ import main

import pytest


def remove_from_dir(param):
    """Remove file(s) if exist."""
    if isinstance(param, str):
        if os.path.exists(param):
            os.remove(param)

    elif isinstance(param, tuple):
        for i in param:
            if os.path.exists(i):
                os.remove(i)


@pytest.fixture(scope='function')
def clean_output(request):
    """Take input of string or tuple and removes the files from dir."""
    remove_from_dir(request.param)
    yield request.param
    remove_from_dir(request.param)


@pytest.fixture(scope="function")
def change_dir(request):
    """Change to the current directory of the test."""
    os.chdir(request.fspath.dirname)


@pytest.fixture(scope='function')
def change_curdir_fixtures(request):
    """Change to the fixtures dir in the current directory of the test."""
    os.chdir(os.path.join(request.fspath.dirname, 'fixtures'))


@pytest.fixture(scope='function')
def change_main_dir_fixtures(request):
    """Change to the tests/main/fixtures dir to run tests."""
    os.chdir(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'tests', 'main', 'fixtures'
        )
    )


@pytest.fixture(scope='function')
def change_dir_base(monkeypatch):
    """Change to the current directory."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))


# @pytest.fixture(scope='function')
# def change_dir_main_fixtures(monkeypatch):
#     """Change to the current directory."""
#     monkeypatch.chdir(os.path.join(os.path.abspath(
#         os.path.dirname(__file__)), 'tests', 'main', 'fixtures'))


@pytest.fixture(scope='function')
def change_dir_main_fixtures(request):
    """Change to the current directory."""
    os.chdir(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'tests', 'main', 'fixtures'
        )
    )


@pytest.fixture(scope='function')
def load_yaml(request):
    """Return dict of yaml input(s) either str or tuple."""
    if isinstance(request.param, str):
        with open(request.param) as f:
            return yaml.load(f)

    if isinstance(request.param, tuple):
        output = []
        for i in request.param:
            with open(i) as f:
                output.append(yaml.load(f))
        return output


@pytest.fixture(scope='session')
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main
