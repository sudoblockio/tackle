from tackle import tackle


def test_docs_build(change_dir_base):
    """Make sure docs build."""
    output = tackle('docs/docs-gen.yaml', no_input=True)
    assert output
