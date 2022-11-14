from tackle import tackle


def test_hook_generate_update_document(change_dir):
    """Check that we can update a section in a document and assert the proper output."""
    output = tackle("basic.yaml")
    with open('expected-output.md') as f:
        expected_output = f.read()
    with open('file.md') as f:
        file = f.read()

    assert output
    assert file == expected_output


def test_hook_generate_update_document_multi_line(change_dir):
    """Check multi-line capability in arg."""
    output = tackle("multi-line.yaml", "update_readme")

    with open('multi-line.md') as f:
        file = f.read()

    assert '| Stuff | A thing |' in file
    assert output
