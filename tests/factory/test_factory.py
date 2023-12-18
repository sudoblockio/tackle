import pytest

from tackle.factory import new_context


def test_factory_new_context():
    context = new_context()

    assert context.path.current.hooks_dir.endswith('.hooks')
    assert context.path.current.file is None


@pytest.mark.parametrize("input", [{'a': 1}, [1, 2]])
def test_factory_new_context_raw_inputs(input):
    context = new_context(raw_input=input)
    assert context.data.raw_input == input
