import pytest

from tackle import tackle


@pytest.mark.parametrize(
    "number,output",
    [
        (1, ["1"]),
        (3, ["fizz"]),
        (5, ["buzz"]),
        (15, ["fizz", "buzz"]),
    ],
)
@pytest.mark.parametrize(
    "file_name",
    [
        'conditionals.yaml',
        'list-append.yaml',
        'list-conditionals.yaml',
        'loop-conditional.yaml',
        'match-case.yaml',
        'validator.yaml',
        # 'block-conditions.yaml',
        # 'else-if.yaml',
    ],
)
def test_fizzbuzz_all(file_name, capsys, number, output):
    tackle(file_name, input=number)
    captured_output = capsys.readouterr().out
    for o in output:
        assert o in captured_output


def test_f():
    tackle('update_readme')
