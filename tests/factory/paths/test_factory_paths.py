from tackle import tackle


def test_factory_paths_calling_directory_preserve():
    """
    Validate that the path is properly passed between tackle contexts between `tackle`
     hook calls.
    """
    output = tackle('outer.yaml')
    assert output['outer_calling_file'].endswith('outer.yaml')
    assert output['outer_calling_file_2'].endswith('outer.yaml')
    assert output['inner']['inner_calling_file'].endswith('outer.yaml')
    assert output['inner']['inner_calling_directory'].endswith('paths')
    assert output['inner']['inner_current_file'].endswith('inner.yaml')


def test_factory_paths_calling_directory_from_subdir(cd):
    cd('adir')
    output = tackle()
    assert output['calling_dir'].endswith('adir')


def test_factory_paths_calling_directory_from_subdir_outer(cd):
    cd('adir')
    output = tackle('some_func')
    assert output['inner']['inner_calling_directory'].endswith('adir')
