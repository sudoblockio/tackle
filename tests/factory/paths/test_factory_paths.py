from tackle import tackle


def test_parser_macros_calling_directory_preserve():
    """
    Validate that the path is properly passed between tackle contexts between `tackle`
     hook calls.
    """
    output = tackle('outer.yaml')
    assert output['outer_calling_file'] == 'outer.yaml'
    assert output['outer_calling_file_2'] == 'outer.yaml'
    assert output['outer_current_file'] == 'outer.yaml'
    assert output['inner']['inner_calling_file'] == 'outer.yaml'
    assert output['inner']['inner_calling_directory'].endswith('paths')
    assert output['inner']['inner_current_file'] == 'inner.yaml'
