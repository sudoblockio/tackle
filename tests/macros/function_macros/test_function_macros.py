import pytest

from tackle import exceptions, tackle
from tackle.macros.function_macros import function_macro, split_on_outer_parentheses
from tackle.types import DEFAULT_HOOK_NAME


@pytest.mark.parametrize(
    "hook_input,expected_output",
    [
        ("a", (False, ["a"])),
        ("(a)", (True, ["a"])),
        ("a(b)", (True, ["a", "b"])),
        ("(a)b(c)", (True, ["a", "b", "c"])),
        ("(a)b(c=e())", (True, ["a", "b", "c=e()"])),
    ],
)
def test_function_macros_split_on_outer_parentheses(hook_input, expected_output):
    """Check the initial splitter only working on outer closed parenthesis."""
    output = split_on_outer_parentheses(hook_input)

    assert output == expected_output


@pytest.mark.parametrize(
    "hook_input,expected_output",
    [
        ('do', {}),
        ('do()', {}),
        ('do(foo)', {'foo': {'type': 'Any'}}),
        ('do(foo str)', {'foo': {'type': 'str'}}),
        ('do(foo str = "bar")', {'foo': {'type': 'str', 'default': 'bar'}}),
        ("do(foo str = 'bar')", {'foo': {'type': 'str', 'default': 'bar'}}),
        ("do(foo int=1)", {'foo': {'type': 'int', 'default': 1}}),
        ("do(foo list=['bar'])", {'foo': {'type': 'list', 'default': ['bar']}}),
        ('do(foo list = [1])', {'foo': {'type': 'list', 'default': [1]}}),
        ("do(foo list[str])", {'foo': {'type': 'list[str]'}}),
        ('do(foo str, bar str)', {'foo': {'type': 'str'}, 'bar': {'type': 'str'}}),
        ('do(foo str | int)', {'foo': {'type': 'str | int'}}),
        ('do(foo str | int = "bar")', {'foo': {'type': 'str | int', 'default': 'bar'}}),
        ('do(foo list[str, int])', {'foo': {'type': 'list[str, int]'}}),
        ('do(foo bar= baz())', {'foo': {'type': 'bar', 'default': 'baz()'}}),
        (
            'do(foo str | int, bar str | int)',
            {'foo': {'type': 'str | int'}, 'bar': {'type': 'str | int'}},
        ),
        ('do(foo="bar")', {'foo': {'type': 'Any', 'default': 'bar'}}),
        ('do(help="foo")', {'help': 'foo'}),
        ('do(foo int, help="foo")', {'foo': {'type': 'int'}, 'help': 'foo'}),
        (
            'do(foo int = "bar", help="foo")',
            {'foo': {'type': 'int', 'default': 'bar'}, 'help': 'foo'},
        ),
    ],
)
def test_function_macros(context, hook_input, expected_output):
    """Check that function dicts are properly parsed."""
    name, function_output, _ = function_macro(context, key_raw=hook_input, value={})

    # Clean out items not tested
    function_output.pop('args', None)
    function_output.pop('exec', None)

    assert name == 'do'
    assert function_output == expected_output


@pytest.mark.parametrize(
    "hook_input,self_name,hook_name",
    [
        ('(f foo)do(bar baz)', 'f', 'foo'),
        ('(foo)do(bar baz)', None, 'foo'),
    ],
)
def test_function_macros_methods(context, hook_input, self_name, hook_name):
    """Test the methods output."""
    _, _, methods = function_macro(context, key_raw=hook_input, value={})

    assert methods['method_name'] == 'do'
    assert methods['self_name'] == self_name
    assert methods['hook_name'] == hook_name


@pytest.mark.parametrize(
    "hook_input,expected_output",
    [
        ('(do', '(do'),
        ('a(do', 'a(do'),
        ('do)ab', 'do)ab'),
        ('do()', 'do'),
        ('do(a b = c())', 'do'),
        ('(foo)do()', None),
        ('(foo)do(a b = c())', None),
        ('(foo)', DEFAULT_HOOK_NAME),
    ],
)
def test_function_macros_hook_name(context, hook_input, expected_output):
    """Test the hook name output."""
    name, _, _ = function_macro(context, key_raw=hook_input, value={})

    assert name == expected_output


@pytest.mark.parametrize(
    "input_file,args",
    [
        ('default-default.yaml', ()),
        ('default-required.yaml', ('world',)),
        ('default-no-type.yaml', ('world',)),
        ('default-string.yaml', ('world',)),
        ('default-string-hook.yaml', ('world',)),
    ],
)
def test_function_macro_defaults(input_file, args):
    output = tackle(input_file, *args)

    assert output == 'Hello world!'


@pytest.mark.parametrize(
    "input_file",
    [
        # 'function-default.yaml',
        # 'function-required.yaml',
        # TODO: Determine if hooks can be
        'hook-default.yaml',
    ],
)
def test_function_macro_function_calls(input_file):
    output = tackle(input_file)

    assert output['call'] == 'Hello universe!'
    assert output['render'] == 'Hello universe!'
    assert output['error'] == 2


@pytest.mark.parametrize(
    "input_file",
    [
        'method-func-inside.yaml',
        # TODO: Functional methods
        # 'method-outside.yaml',
    ],
)
def test_function_macro_method_calls(input_file):
    output = tackle(input_file)

    assert output['call'] == 'Hello universe!'
    assert output['render'] == 'Hello universe!'
    assert output['error'] == 2


@pytest.mark.parametrize(
    "hook_input,expected_exception",
    [
        # Can't have a default before a required arg - messes up positional settings
        ('do(foo bar=baz(), bin)', exceptions.MalformedHookDefinitionException),
        # Three closed parenthesis no good
        ('()do(foo bar baz)()', exceptions.MalformedHookDefinitionException),
    ],
)
def test_function_macro_exceptions(context, hook_input, expected_exception):
    """Check exceptions are thrown."""
    with pytest.raises(expected_exception=expected_exception):
        function_macro(context, hook_input, value={})
