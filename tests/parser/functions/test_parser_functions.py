import pytest

from tackle import tackle


@pytest.mark.parametrize(
    "fixture",
    [
        'no-arg.yaml',
        # 'no-arg-str-val.yaml',
        # 'arg-default.yaml',
        # 'arg-default-val.yaml',
    ],
)
def test_parser_functions_(fixture):
    output = tackle(fixture)

    assert output['call'] == 'foo'
