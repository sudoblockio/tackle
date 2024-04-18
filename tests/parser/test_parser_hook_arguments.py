from typing import Type

from tackle import BaseHook
from tackle.factory import new_context
from tackle.parser import evaluate_args


def run_evaluate_args(args: list, Hook: Type[BaseHook]):
    context = new_context()
    context.hooks.public['my_hook'] = Hook

    hook_dict = {}

    evaluate_args(context=context, args=args, hook_dict=hook_dict, Hook=Hook)
    return hook_dict


def test_parser_evaluate_args_single_str():
    class MyHook(BaseHook):
        hook_name = 'my_hook'
        foo: str
        args: list = ['foo']

    input_args = ['bar']
    output = run_evaluate_args(args=input_args, Hook=MyHook)

    assert output == {'foo': 'bar'}


def test_parser_evaluate_args_many_str():
    class MyHook(BaseHook):
        hook_name = 'my_hook'
        foo: str
        bar: str
        baz: str
        args: list = ['foo', 'bar', 'baz']

    args = ['one', 'two', 'three']
    output = run_evaluate_args(args=args, Hook=MyHook)

    assert output == {'foo': 'one', 'bar': 'two', 'baz': 'three'}


def test_parser_evaluate_args_joined_str():
    class MyHook(BaseHook):
        hook_name = 'my_hook'
        foo: str
        bar: str
        args: list = ['foo', 'bar']

    args = ['one', 'two', 'three', 'four']
    output = run_evaluate_args(args=args, Hook=MyHook)

    assert output == {'foo': 'one', 'bar': 'two three four'}


def test_parser_evaluate_args_joined_list():
    class MyHook(BaseHook):
        hook_name = 'my_hook'
        foo: str
        bar: list
        args: list = ['foo', 'bar']

    args = ['one', 'two', 'three', 'four']
    output = run_evaluate_args(args=args, Hook=MyHook)

    assert output == {'foo': 'one', 'bar': ['two', 'three', 'four']}


def test_parser_evaluate_args_overflow_bool_error():
    # TODO: This should be an error?
    class MyHook(BaseHook):
        hook_name = 'my_hook'
        foo: bool
        args: list = ['foo']

    args = [True, False]
    output = run_evaluate_args(args=args, Hook=MyHook)

    assert output == {'foo': True}
