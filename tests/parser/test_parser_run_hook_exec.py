from tackle.parser import run_hook_exec
from tackle.factory import new_context
from tackle.models import HookCallInput


def test_run_hook_exec():
    """When a hook is called that does not need any supplied params it works."""
    context = new_context()
    context.data.public = {'foo': 'bar'}
    hook = context.hooks.native['literal'](input='foo')
    hook_call = HookCallInput()

    output = run_hook_exec(context=context, hook_call=hook_call, hook=hook)
    assert output == 'foo'


def test_run_hook_exec_context():
    """When a hook is called that does need supplied params such as context it works."""
    context = new_context()
    context.data.public = {'foo': 'bar'}
    hook = context.hooks.native['set'](path='foo', value='baz')
    hook_call = HookCallInput()

    run_hook_exec(context=context, hook_call=hook_call, hook=hook)
    assert context.data.public['foo'] == 'baz'


def test_run_hook_exec_context_quoted():
    """
    Sometimes the user will be quoting the type - ie def call(self, context: 'Context')
     so we need to account for this.
    """
    context = new_context()
    context.data.public = {'foo': 'bar'}
    hook = context.hooks.native['var'](input='{{foo}}')
    hook_call = HookCallInput()

    output = run_hook_exec(context=context, hook_call=hook_call, hook=hook)
    assert output == 'bar'
