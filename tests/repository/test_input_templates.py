"""Tests for various input templates."""
import os
from tackle.main import tackle


def test_call_with_context_file(change_dir_main_fixtures):
    """Test that we can call a context file directly - ie `tackle somefile.yaml`."""
    o = tackle(os.path.join('extra-contexts', 'fake-repo-pre.yaml'), no_input=True)
    assert o
