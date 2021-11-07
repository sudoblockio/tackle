from tackle import tackle


def test_context_multiple_args(change_curdir_fixtures):
    output = tackle('args.yaml', no_input=True)
    assert output['two_args'] == 'foo bar'
    assert output['three_args'] == 'foo bar baz'


def test_context_tackle_in_tackle(change_curdir_fixtures):
    output = tackle('outer_tackle.yaml', no_input=True)
    assert output['outer']['inner'] == 'this'


def test_context_tackle_in_tackle_arg(change_curdir_fixtures):
    output = tackle('outer_tackle_arg.yaml', no_input=True)
    assert output['outer']['inner'] == 'this'


def test_context_no_input(change_curdir_fixtures):
    output = tackle('outer_tackle.yaml', no_input=True)
    assert output['outer']['inner'] == 'this'
