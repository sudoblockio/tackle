from tackle import tackle


def test_render_globals_base(cd_fixtures):
    """
    Verify that when we have a variable in the context, for instance `namespace`, that
     we are able to render it from the context.
    """
    # TODO: This will fix itself when hook call keys have a list of renderables which
    #  used to imply that the list should be rendered
    output = tackle('globals.yaml')
    for i in output['globals_raw']:
        assert i == 'stuff'


def test_render_hooks_with_args(cd_fixtures):
    """Verify that we can call hooks without args."""
    output = tackle('hooks-args.yaml')
    assert output['get_default'] == 'things'
    assert output['get_sep'] == 'things'
    assert 'tmp' in output['nested']
    assert output['nested_test']['and'] == 'things'
