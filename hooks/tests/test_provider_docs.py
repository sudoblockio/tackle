import os.path
import sys
import pytest

from tackle import tackle, get_hook
from hooks.provider_docs import hook_field_type_to_string

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
    output = hook_field_type_to_string(type_)
    assert output == expected_output


PROVIDERS_PATH = os.path.join('..', '..', 'providers')

def get_provider_paths(provider_name: str = None):
    if provider_name is not None:
        return [os.path.join(PROVIDERS_PATH, provider_name)]

    output = []
    for i in os.listdir(PROVIDERS_PATH):
        if os.path.isdir(os.path.join(PROVIDERS_PATH, i)) and i != '__pycache__':
            output.append(os.path.join(PROVIDERS_PATH, i))
    return output


@pytest.mark.parametrize("provider_path", get_provider_paths())
def test_provider_docs_hook(provider_path):
    """Check that we can run the collections provider."""
    Hook = get_hook('provider_docs')
    output = Hook(path=provider_path).exec()

    assert len(output['hooks']) > 0


def test_provider_tackle_provider_docs():
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
