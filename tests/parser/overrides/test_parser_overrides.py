# import pytest
#
# from tackle import tackle, exceptions
# from tackle.cli import main
#
#
# def test_parser_overrides_dict_input():
#     """
#     Test bringing in an input dict along with a target which should be interpreted as
#      overriding keys to the target.
#     """
#     override_dict = {
#         'this': 1,
#         'that': 1,
#         'this_private': 1,
#         'that_private': 1,
#         'foo': 1,  # Non-hook key
#         'stuff': 'things',  # Missing key
#     }
#
#     output = tackle('dict-input.yaml', **override_dict)
#     for _, v in output.items():
#         assert v == 1
#     assert output['this'] == 1
#
#
# def test_parser_overrides_dict_input_main(capsys):
#     """Test same as above but from command line."""
#     main(
#         [
#             "dict-input.yaml",
#             "--this",
#             "1",
#             "--that",
#             "2",
#             "--this_private",
#             "1",
#             "--that_private",
#             "2",
#             "--print",
#         ]
#     )
#     assert 'this' in capsys.readouterr().out
#
#
# def test_parser_overrides_dict_embedded():
#     override_dict = {
#         'this': {
#             'that': 1,
#         },
#     }
#
#     output = tackle('dict-input.yaml', **override_dict)
#     assert output['this']['that'] == 1
#
#
# def test_main_overrides_str_for_block():
#     """Test that we can override inputs in a block."""
#     o = tackle("block-input.yaml", overrides="block-input-overrides.yaml")
#     # Should normally throw error with prompt
#     assert o['foo']['this'] == "stuff"
#     assert o['bar'] == 'baz'
#
#
# @pytest.mark.parametrize("input_file", [
#     "dcl-hook-input.yaml",
#     "dcl-hook-exec-input.yaml",
# ])
# def test_main_overrides_str_for_func(input_file):
#     """Test that we can override inputs for a default hook."""
#     o = tackle(input_file, overrides="dict-input-overrides.yaml")
#     # Should normally throw error with prompt
#     assert o['this'] == "stuff"
#
#
# def test_main_input_dict_to_overrides(mocker):
#     """
#     Test bringing in an input dict along with a target which should be interpreted as
#      overriding keys to the target.
#     """
#     mock = mocker.patch("tackle.main.parse_context")
#     input_dict = {'this': 1}
#
#     ctx = tackle(return_context=True, **input_dict)
#     assert mock.called
#     assert ctx.input.kwargs == input_dict
#
#
# def test_main_overrides_str():
#     """Test that we can override inputs."""
#     o = tackle("dict-input.yaml", overrides="dict-input-overrides.yaml")
#     # Should normally throw error with prompt
#     assert o['this'] == "stuff"
#     # Again, should raise error w/o override
#     # main(["dict-input.yaml", "--override", "dict-input-overrides.yaml"])
#
#
# def test_main_overrides_str_not_found_error():
#     """Test that we get error on ."""
#     with pytest.raises(exceptions.UnknownSourceException):
#         tackle("dict-input.yaml", overrides="not-exists")
