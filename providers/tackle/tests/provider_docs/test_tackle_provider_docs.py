import sys
import pytest

from tackle import tackle
from tackle.providers.tackle.hooks.provider_docs import hook_type_to_string

from typing import Dict, List, Union, Any

TYPE_FIXTURES = [
    (dict, "dict"),
    # (Dict, "dict"),
    (list, "list"),
    # (List, "list"),
    (Union[dict, list], "union"),
    (Any, "any"),
]


@pytest.mark.parametrize("type_,expected_output", TYPE_FIXTURES)
def test_hook_type_to_string(type_, expected_output):
    output = hook_type_to_string(type_)
    assert output == expected_output


def test_provider_tackle_provider_docs(change_dir):
    """Run the provider docs."""
    if sys.version_info.minor <= 6:
        return

    output = tackle('docs.yaml')
    assert (
        len(
            [
                i
                for i in output['render_context']['hooks']
                if i['hook_type'] == 'provider_docs'
            ]
        )
        == 1
    )
