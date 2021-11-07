# import pytest
#
# from tackle.parser.source import unpack_args_kwargs
# from tackle.models import Context
#
# # @pytest.fixture()
# # def cli_inputs()
#
# TEMPLATES = [
#     ('foo bar baz', 2, 0, 0),
#     ('foo bar baz bing', 3, 0, 0),
#     ('foo bar --baz foo', 1, 1, 0),
#     ('foo bar --baz foo --bing baz', 1, 2, 0),
#     ('foo --bar baz', 0, 1, 0),
#     ('foo bar --baz', 1, 0, 1),
#     ('foo bar baz --bing', 2, 0, 1),
#     ('foo --bar baz --foo', 0, 1, 1),
#     ('foo bar --baz foo --bing --baz bling', 1, 2, 1),
#     ('foo --bar baz blah --bling', 1, 1, 1),
#     ('foo --bar --baz', 0, 0, 2),
# ]
#
#
# @pytest.mark.parametrize("template,len_args,len_kwargs,len_flags", TEMPLATES)
# def test_unpack_args_kwargs(template, len_args, len_kwargs, len_flags):
#     c = Context(template=template)
#     unpack_args_kwargs(c)
#
#     assert len_args == len(c.command_args)
#     assert len_kwargs == len(c.command_kwargs)
#     assert len_flags == len(c.command_flags)
