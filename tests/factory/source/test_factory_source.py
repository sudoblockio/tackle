import os
import shutil
import tempfile
from pathlib import Path

import pytest

from tackle import exceptions, main
from tackle.context import Context, InputArguments
from tackle.factory import new_inputs, new_source
from tackle.settings import settings

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
    # Check that the full path is in the source.file
    assert 'factory' in source.file
    assert source.hooks_dir is None


def test_factory_source_new_source_find_in_parent_arg(cd):
    """When we are given a find_in_parent_arg, find source in parent."""
    cd('a-dir-with-tackle')
    context = Context(
        input=InputArguments(
            args=[{'foo': 'bar'}],
            kwargs={},
        ),
    )
    source = new_source(find_in_parent=True, context=context)
    assert source.base_dir.endswith('source')
    assert source.file.endswith('tackle.yaml')
    assert 'tests' in source.file
    # Args should be reinserted
    assert context.input.args[0] == {'foo': 'bar'}
    assert source.hooks_dir is None


def test_factory_source_new_source_dict_arg():
    """When the first arg is an list or dict arg, insert it as raw."""
    source = new_source(
        context=Context(
            input=InputArguments(
                args=[{'foo': 'bar'}],
                kwargs={},
            ),
        )
    )
    assert source.raw == {'foo': 'bar'}
    assert source.hooks_dir is None


def test_factory_source_new_source_int_arg():
    """
    When the first arg is an int / float / bool (not str, dict, list) then we need to
     find the closest tackle provider and reinsert the arg into the args.
    """
    source = new_source(
        context=Context(
            input=InputArguments(
                args=[1],
                kwargs={},
            ),
        )
    )
    # Source is the tackle file in the current directory
    assert source.base_dir.endswith('source')
    assert source.hooks_dir is None


def test_factory_source_new_source_zip(cd):
    """Check that zip providers work. Will run the unzipped provider in a tmp dir."""
    cd('zip')
    source = new_source(
        context=Context(
            input=InputArguments(
                args=['zipped-provider.zip'],
                kwargs={},
            ),
        )
    )
    assert os.path.exists(source.directory)
    # Actually unzips in a tmp dir
    if source.directory.endswith('zipped-provider'):
        shutil.rmtree(source.directory)
    assert source.file.endswith('tackle.yaml')
    assert 'zipped-provider' in source.file
    assert not source.find_in_parent
    assert source.hooks_dir is None


@pytest.fixture()
def repo_path():
    path = Path(os.path.join(settings.providers_dir, 'test', 'bar', 'tackle.yaml'))
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
        ),
    )
    assert source.directory == repo_path == source.base_dir
    assert source.file.endswith('tackle.yaml')
    assert not source.find_in_parent
    assert source.hooks_dir is None
    assert mock.called
    assert source.hooks_dir is None


def test_factory_source_new_source_with_directory():
    """Check we can supply a directory argument."""
    context = Context(input=InputArguments(args=[], kwargs={}))
    source = new_source(context=context, directory='a-dir')

    assert source.base_dir.endswith('source')
    assert source.directory.endswith('a-dir')
    assert source.file.endswith('tackle.yaml')
    assert 'tests' in source.file
    assert source.hooks_dir is None


def test_factory_source_new_source_with_file():
    """Check we can supply a file argument."""
    context = Context(input=InputArguments(args=[]))
    source = new_source(context=context, file='a-file.yaml')

    assert source.base_dir.endswith('source')
    assert source.directory == source.base_dir
    assert source.file.endswith('a-file.yaml')
    assert 'tests' in source.file
    assert source.hooks_dir is None


def test_factory_source_new_source_with_file_arg():
    """Check we can supply a file argument."""
    path = os.path.join('a-dir-with-file', 'a-file.yaml')
    context = Context(input=InputArguments(args=[path]))
    source = new_source(context=context)

    assert source.base_dir.endswith('a-dir-with-file')
    assert source.directory == source.base_dir
    assert source.file.endswith('a-file.yaml')
    assert 'tests' in source.file
    assert source.hooks_dir is None


def test_factory_source_as_dict():
    """Check we can supply a raw input. Updates the data object with the argument."""
    context = Context(input=InputArguments(args=[{'foo': 1}], kwargs={}))

    source = new_source(context=context)

    # Should be without any data in it but still initialized
    assert source.file is None
    assert source.hooks_dir is None


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


@pytest.fixture(scope='function')
def run_in_temp_dir(cd):
    temp_dir = tempfile.mkdtemp()
    cd(temp_dir)


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
    When supplying the f flag and inside a tmp dir where there is no tackle
     provider in the parent dir should raise.
    """
    context = Context(input=InputArguments(args=[]))
    with pytest.raises(exceptions.UnknownSourceException):
        new_source(context=context, find_in_parent=True)


def test_factory_source_new_source_exception_find_in_parent_repo_does_not_exist(cd):
    """Tackle invocation with non-exist repository should raise error."""
    if os.name != 'nt':
        cd('/')
    else:
        cd('\\')
    with pytest.raises(exceptions.UnknownSourceException) as info:
        main.tackle('definitely-not-a-valid-repo-dir')

    assert 'definitely-not-a-valid-repo-dir' in info.value.message
