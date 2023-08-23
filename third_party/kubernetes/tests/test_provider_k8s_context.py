import os
import pytest

from tackle.main import tackle


@pytest.fixture()
def set_kubeconfig():
    # fmt: off
    os.environ["KUBECONFIG"] = ':'.join([os.path.join(os.path.abspath(os.path.dirname(__file__)), f'kubeconfig{i}.yaml') for i in ['', '2']])
    # fmt: on


def test_provider_k8s_context(change_dir, set_kubeconfig):
    output = tackle('context.yaml', no_input=True)
    assert 'federal-context' in output['context_map']
    assert output['context'] == 'federal-context'
