from tackle import tackle


###############
# Default hooks
###############
def test_function_default_hook_no_context(chdir):
    """Validate that we can run a default hook."""
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-no-context.yaml')
    assert output['p'] == 'things'


def test_function_default_hook_no_context_kwargs(chdir):
    """Validate that we can run a default hook with a kwarg."""
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-no-context.yaml', stuff='bar')
    assert output['p'] == 'bar'
    assert output['b']


def test_function_default_hook_no_context_flags(chdir):
    """
    Validate that flags are interpreted properly. In this case the default is true so
    when setting the flag, it should be false.
    """
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-no-context.yaml', global_flags=['things'])
    assert isinstance(output['b'], bool)
    assert not output['b']


def test_function_default_hook_context(chdir):
    """Test that outer context is additionally parsed with the default hook."""
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-context.yaml')
    assert output['p'] == 'things'
    assert output['foo'] == 'bar'


def test_function_default_hook_no_context_method_call(chdir):
    """Validate that we can run a default hook."""
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-no-context.yaml', 'do')
    assert output['d'] == 'baz'


def test_function_default_hook_no_context_method_call_args(chdir):
    """Validate that we can run a default hook."""
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-no-context.yaml', 'do', 'bizz')
    assert output['d'] == 'bizz'


def test_function_default_hook_embedded(chdir):
    """Validate that we can run a default hook embedded methods."""
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-embedded.yaml', 'do', 'stuff', 'things')
    assert output['t'] == 'bar'


def test_function_default_hook_embedded_kwargs(chdir):
    """Validate that we can run a default hook embedded methods with kwargs."""
    chdir('cli-fixtures')
    output = tackle(
        'cli-default-hook-embedded.yaml', 'do', 'stuff', 'things', foo='bing'
    )
    assert output['t'] == 'bing'


def test_function_default_hook_embedded_kwargs_full(chdir):
    """Validate that we can run a default hook embedded methods with kwargs schema."""
    chdir('cli-fixtures')
    output = tackle('cli-default-hook-embedded.yaml', 'do', 'stuff', foo_full='bing')
    assert output['t'] == 'bing'


#############
# Non-default
#############
def test_function_cli_hook_arg(chdir):
    """Validate that we can run a default hook with an arg."""
    chdir('cli-fixtures')
    output = tackle('cli-hook-no-context.yaml', 'run')
    assert output['t'] == 'things'
    assert output['s']


def test_function_cli_hook_arg_args(chdir):
    """Validate that we can run a default hook with an arg."""
    chdir('cli-fixtures')
    output = tackle('cli-hook-no-context.yaml', 'run', 'do', 'bazzz')
    assert output['d'] == 'bazzz'
    assert output['t'] == 'things'
    assert output['s']


def test_function_cli_hook_arg_kwargs(chdir):
    """Validate that we can run a default hook with an arg."""
    chdir('cli-fixtures')
    output = tackle('cli-hook-no-context.yaml', 'run', stuff='bazzz')
    assert output['t'] == 'bazzz'
    assert output['s']


def test_function_cli_hook_arg_flags(chdir):
    """Validate that we can run a default hook with an arg."""
    chdir('cli-fixtures')
    output = tackle('cli-hook-no-context.yaml', 'run', global_flags=['things'])
    assert not output['s']


def test_function_hook_embedded_kwargs(chdir):
    """Validate that we can run a default hook embedded methods with kwargs."""
    chdir('cli-fixtures')
    output = tackle(
        'cli-default-hook-embedded.yaml', 'run', 'do', 'stuff', 'things', foo='bing'
    )
    assert output['t'] == 'bing'
