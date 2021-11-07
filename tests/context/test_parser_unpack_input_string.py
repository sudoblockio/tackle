import pytest
from tackle.utils.command import unpack_args_kwargs


FIXTURES = [
    ("this --if \"expanded == 'that'\"", ["this"], {"if": "expanded == 'that'"}, []),
    (
        "this that --if \"expanded == 'that'\"",
        ["this"],
        {"if": "expanded == 'that'"},
        [],
    ),
]


@pytest.mark.parametrize("input_string,args,kwargs,flags", FIXTURES)
def test_unpack_input_string(input_string, args, kwargs, flags):
    args_out, kwargs_out, flags_out = unpack_args_kwargs(input_string)
    assert args_out == args
    assert kwargs_out == kwargs
    assert flags_out == flags
