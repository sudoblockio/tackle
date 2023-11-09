import os
from pathlib import Path
import pytest
import shutil

from tackle import exceptions
from tackle.factory import new_source, new_inputs
from tackle.context import InputArguments, Context
from tackle.settings import settings

"""
TODO: Make paths consistent
 https://github.com/sudoblockio/tackle/issues/175
"""

@pytest.fixture()
def source_fixtures(chdir):
    chdir('source-fixtures')


INPUT_FIXTURES: list[[list]] = [
    # ([None]),
    ([]),
    (['.']),
    (['a-dir']),
    # Here we are testing that the arg resolves to the parent tackle and will
    # later be consumed as an arg which new_source does not check.
    (['something-that-does-not-exist']),
]


@pytest.mark.parametrize("args", INPUT_FIXTURES)
def test_factory_source_new_source_parameterized(args):
    """
    Check various input args resolve to a tackle provider in current dir or in parent
     (ie base of this repo).
    """
    context = Context(input=new_inputs(args=args))
    source = new_source(context=context)
    # Base tackle is `.tackle.yaml`
    assert source.file.endswith('tackle.yaml')


@pytest.fixture()
def repo_path():
    path = Path(os.path.join(settings.provider_dir, 'test', 'bar', 'tackle.yaml'))
    shutil.rmtree(path, ignore_errors=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    yield path.parent
    shutil.rmtree(path, ignore_errors=True)


def test_factory_source_new_source_repo(mocker, repo_path):
    """Check that remote providers work (ie github org/repo)."""
    mock = mocker.patch(
        'tackle.factory.get_repo_source',
        autospec=True,
        return_value=repo_path,
    )
    source = new_source(
        latest=True,
        context=Context(
            input=InputArguments(
                args=['test/bar'],
                kwargs={},
            ),
        ))
    assert source.directory == repo_path == source.base_dir
    assert source.file.endswith('tackle.yaml')
    assert not source.find_in_parent
    assert source.hooks_dir is None
    assert mock.called


def test_factory_source_new_source_zip(cd):
    """Check that zip providers work. Will run the unzipped provider in a tmp dir."""
    cd(os.path.join('', 'zip'))
    source = new_source(
        context=Context(
            input=InputArguments(
                args=['zipped-provider.zip'],
                kwargs={},
            ),
        ))
    assert os.path.exists(source.directory)
    # Actually unzips in a tmp dir
    shutil.rmtree(source.directory)
    assert source.file.endswith('tackle.yaml')
    assert not source.find_in_parent


def test_factory_source_new_source_with_directory():
    """Check we can supply a directory argument."""
    context = Context(input=InputArguments(args=[], kwargs={}))
    source = new_source(context=context, directory='a-dir')

    assert source.base_dir.endswith('source')
    assert source.directory.endswith('a-dir')
    assert source.file.endswith('tackle.yaml')


def test_factory_source_new_source_with_file():
    """Check we can supply a file argument."""
    context = Context(input=InputArguments(args=[]))
    source = new_source(context=context, file='a-file.yaml')

    assert source.base_dir.endswith('source')
    assert source.directory == source.base_dir
    assert source.file.endswith('a-file.yaml')


def test_factory_source_as_dict():
    """Check we can supply a raw input. Updates the data object with the argument."""
    context = Context(input=InputArguments(args=[{'foo': 1}], kwargs={}))

    source = new_source(context=context)

    # Should be without any data in it but still initialized
    assert source.file is None


EXCEPTION_FIXTURES = [
    ([], {'file': 'does-not-exist'}),
    ([], {'directory': 'does-not-exist'}),
]


@pytest.mark.parametrize("args,kwargs", EXCEPTION_FIXTURES)
def test_factory_source_new_source_exceptions_parameterized(args, kwargs):
    """When file / directory flag inputs don't exist, raise."""
    context = Context(input=InputArguments(args=args))
    with pytest.raises(exceptions.UnknownSourceException):
        new_source(context=context, **kwargs)


def test_factory_source_new_source_exception_no_arg_temp_di(run_in_temp_dir):
    """
    When no arg is supplied it tries to find in parent. This test is run in temp dir
     so there will be no tackle base and should raise.
    """
    context = Context(input=InputArguments(args=[]))
    with pytest.raises(exceptions.UnknownSourceException):
        new_source(context=context)



def test_factory_source_new_source_exception_find_in_parent(run_in_temp_dir):
    """
    When supplying the find_in_parent flag and inside a tmp dir where there is no tackle
     provider in the parent dir should raise.
    """
    context = Context(input=InputArguments(args=[]))
    with pytest.raises(exceptions.UnknownSourceException):
        new_source(context=context, find_in_parent=True)