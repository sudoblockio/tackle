import pytest

from tackle import tackle, exceptions


@pytest.mark.parametrize("hook_name, hook_args, assertion", [
    ("required_input", ["bar"], lambda x: x == "bar"),
    ("takes_context_and_var", ["bar"], lambda x: "tests" in x),
])
def test_decorators_hook_tackle_args(hook_name, hook_args, assertion):
    output = tackle(hook_name, *hook_args)
    assert assertion(output)


@pytest.mark.parametrize("hook_name, hook_kwargs, assertion", [
    ("no_inputs", {}, lambda x: x == "bar"),
    ("required_input", {"foo": "bar"}, lambda x: x == "bar"),
    ("non_required_input", {}, lambda x: x == "bar"),
    ("public_hook", {}, lambda x: x == "bar"),
    ("takes_context", {}, lambda x: "tests" in x),
    ("takes_context_and_var", {"foo": "bar"}, lambda x: "tests" in x),
])
def test_decorators_hook_tackle_kwargs(hook_name, hook_kwargs, assertion):
    output = tackle(hook_name, **hook_kwargs)
    assert assertion(output)


@pytest.mark.parametrize("hook_name, hook_args, hook_kwargs, exception", [
    ("no_inputs", ["bar"], {}, exceptions.UnknownHookInputArgumentException),
    ("required_input", [], {}, exceptions.MalformedHookFieldException),
])
def test_decorators_hook_tackle_errors(hook_name, hook_args, hook_kwargs, exception):
    with pytest.raises(exception):
        tackle(hook_name, *hook_args, **hook_kwargs)
