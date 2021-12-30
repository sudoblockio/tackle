"""Test hook model."""
from tackle.models import BaseHook
import logging

LOGGER = logging.getLogger(__name__)


def test_base_hook_init():
    """Test instantiating a hook."""
    inp = {
        'hook_type': 'foo',
        # 'foo': 'bar',
        'else': 'foo',
        'merge': True,
        'if': 'stuff == things',
    }

    h = BaseHook(**inp)
    # assert h.hook_type == 'foo'
    assert h.if_ == '{{stuff == things}}'
    assert h.merge
    assert isinstance(h.merge, bool)


# def test_hook_dict_match_case(caplog):
#     inp = {
#         'match': 'foo',
#         'case': ['bar', '_'],
#     }
#     h = BaseHook(**inp)
#     if sys.version_info[1] >= 10:
#         assert h.match_ == 'foo'
#
#     if sys.version_info[1] <= 10:
#         assert h.match_ is None
#
#     # TODO: Fix this test
# log_output = caplog.text
# assert 'Must be using Python' in caplog.text
