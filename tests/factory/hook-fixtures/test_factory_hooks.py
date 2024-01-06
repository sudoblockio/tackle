import os

import pytest
from pydantic._internal._model_construction import ModelMetaclass

from tackle.context import Context, Data, Source
from tackle.factory import create_hooks
from tackle.models import LazyBaseHook


def test_factory_import_native_providers():
    """Test that we can import a hook ('foo', 'Base') from a hooks dir."""
    context = Context(
        source=Source(hooks_dir='../.hooks', name='foo'),
        data=Data(),
    )
    create_hooks(context=context)

    assert len(context.hooks.native.keys()) > 50
    assert isinstance(context.hooks.private['foo'], ModelMetaclass)
    assert isinstance(context.hooks.public['Base'], LazyBaseHook)


def test_factory_hooks_create_hooks(patch_native_provider_import):
    """Test basic usage."""
    context = Context(source=Source())
    create_hooks(context=context)
    assert context.hooks.public == {}
    assert len(context.hooks.native) > 80


@pytest.fixture()
def patch_import_hooks_from_hooks_directory(mocker):
    mock = mocker.patch(
        'tackle.factory.import_hooks_from_hooks_directory',
        autospec=True,
    )
    yield mock
    # assert mock.called


def test_factory_hooks_create_hooks_with_hooks(
    patch_import_hooks_from_hooks_directory,
    base_dir,
):
    """Test basic usage."""
    context = Context(source=Source())
    create_hooks(context=context, hooks_dir=os.path.join(base_dir, '../.hooks'))
    patch_import_hooks_from_hooks_directory.assert_called_once()
    # TODO: Fix this - it should have some public hooks
    assert context.hooks.public == {}
