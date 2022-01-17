"""test for provider_docs hook."""
import sys

from tackle import tackle


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
