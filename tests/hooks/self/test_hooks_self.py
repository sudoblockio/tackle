from tackle import tackle


def test_hooks_method_call_self():
    """"""
    o = tackle('call-self.yaml')
    assert o
