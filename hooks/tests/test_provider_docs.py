import pytest
import os.path

from tackle import tackle, get_hook, Context

PROVIDERS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'providers')


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
    output = Hook(path=provider_path).exec(context=Context())

    assert len(output['hooks']) > 0


def test_local_hooks_generate_provider_docs():
    """Generate the provider docs."""
    output = tackle('gen_docs')
    paths = [
        'provider_dir',
        'provider_docs_dir',
        'schemas_dir',
        'templates_dir',
    ]

    for p in paths:
        assert os.path.exists(output[p])

    assert len(output['gen']) > 10
