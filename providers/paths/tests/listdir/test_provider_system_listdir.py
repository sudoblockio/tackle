from tackle import tackle


def test_provider_system_hook_listdir():
    output = tackle()

    assert len(output['string_input']) == 3
    assert len(output['string_input_sorted']) == 2
    assert len(output['list_input']) == 2
    assert 'dir1' in output['only_directories']
    assert 'things.py' in output['only_files']
    assert 'things.py' not in output['only_directories']
    assert 'dir1' not in output['only_files']
    assert '.hidden-dir' not in output['ignore_hidden']
    assert '.hidden-dir' not in output['ignore_hidden_directories']
    assert '.hidden-stuff' in output['ignore_hidden_directories']
    assert '.hidden-dir' in output['ignore_hidden_files']
    assert '.hidden-dir' in output['exclude_files_str']
    assert 'dir1' not in output['exclude_files_str']
    assert 'dir1' not in output['exclude_files_list']
    assert 'dir2' not in output['exclude_files_list']
    assert 'dir1' not in output['exclude_files_str_re']
    assert 'dir2' not in output['exclude_files_str_re']
