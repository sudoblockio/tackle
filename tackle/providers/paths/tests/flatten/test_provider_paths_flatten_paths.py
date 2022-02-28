from tackle.main import tackle


def test_provider_paths_flatten(change_dir):
    output = tackle()
    assert output['flattened'][0] == 'one/baz/stuff.yaml'
    assert output['flattened'][9] == 'complex/alist/another_list/things.py'
    assert output['flattened_base'][0] == 'base/path/one/baz/stuff.yaml'
    assert output['flattened_base_list'][0] == 'base/path/foo/bar.py'
