import os
from tackle import tackle


def test_docs_build(change_base_dir):
    """Make sure docs build."""
    output = tackle('gen_docs_poc', no_input=True)

    paths = [
        'provider_dir',
        'provider_docs_dir',
        'schemas_dir',
        'templates_dir',
    ]

    for p in paths:
        os.path.exists(output[p])

    assert output
