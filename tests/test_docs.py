from tackle import tackle


def test_docs_build(change_dir_base):
    output = tackle('docs/docs-gen.yaml')
    assert output
