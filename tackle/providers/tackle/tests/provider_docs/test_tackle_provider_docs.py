"""test for provider_docs hook."""
from tackle import tackle


def test_provider_tackle_provider_docs(change_dir):
    """Run the provider docs."""
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
