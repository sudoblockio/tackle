import pytest

from tackle.parser import split_input_data
from tackle.factory import new_context

SPLIT_INPUT_FIXTURES: list[tuple[dict, tuple[int, int, int]]] = [
    (
        {
            'pre': 1,
            'a_hook<-': {1: 1},
            'post': 1,
        },
        (1, 1, 1),
    ),
    (
        {
            'pre1': 1,
            'pre2': 1,
            'a_hook_1<-': {1: 1},
            'post1': 1,
            'a_hook_2<-': {1: 1},
            'post2': 1,
        },
        (2, 2, 2),
    ),
    (
        {
            'a_hook_1<-': {1: 1},
            'post1': 1,
            'post2': 1,
            'post3': 1,
            'a_hook_2<-': {1: 1},
            'post4': 1,
        },
        (0, 4, 2),
    ),
    (
        {
            'a_hook_1<-': {1: 1},
            'post1': 1,
            'post2': 1,
            'post3': 1,
            'a_hook_2<-': {1: 1},
        },
        (0, 3, 2),
    ),
    (
        {
            'a_hook_1<-': {1: 1},
        },
        (0, 0, 1),
    ),
]


@pytest.mark.parametrize("raw_input,counts", SPLIT_INPUT_FIXTURES)
def test_split_input_data(raw_input, counts):
    context = new_context()
    context.data.raw_input = raw_input
    split_input_data(context=context)

    assert len(context.data.pre_input) == counts[0]
    assert len(context.data.post_input) == counts[1]
    assert len(context.hooks.public) == counts[2]
