from tackle import tackle


def test_main_input_dict_to_overrides():
    """
    Test bringing in an input dict along with a target which should be interpreted as
     overriding keys to the target.
    """
    input_dict = {
        'this': 1,
        'that': 2,
        'this_private': 1,
        'that_private': 2,
        'stuff': 'things',  # Missing key
        'foo': 2,  # Non-hook key
    }

    output = tackle('dict-input.yaml', return_context=True, **input_dict)
    assert output['this'] == 1


def test_main_from_cli_input_dict(cd_fixtures, capsys):
    """Test same as above but from command line."""
    main(
        [
            "dict-input.yaml",
            "--this",
            "1",
            "--that",
            "2",
            "--this_private",
            "1",
            "--that_private",
            "2",
            "--print",
        ]
    )
    assert 'this' in capsys.readouterr().out
