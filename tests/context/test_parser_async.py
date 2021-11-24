import yaml
import pytest
import asyncio

import yaml

from tackle.models import Context
from tackle.parser_async import walk_elements, is_tackle_function


FIXTURES = [
    ('tackle_map_new.yaml', 'tackle_map_output.yaml'),
    # ('tackle_map_root.yaml', 'tackle_map_root_output.yaml'),
    # ('tackle_import.yaml', 'petstore.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
@pytest.mark.asyncio
async def test_some_asyncio_code(change_curdir_fixtures, fixture, expected_output):
    with open(fixture) as f:
        fixture = yaml.safe_load(f)

    res = await walk_elements(fixture, [])


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_async_walk_run_until_complete(
    change_curdir_fixtures, fixture, expected_output
):
    loop = asyncio.get_event_loop()

    with open(fixture) as f:
        input_dict = yaml.safe_load(f)

    context = Context(input_dict=input_dict)
    # loop.run_until_complete(asyncio.gather(walk_elements(input_dict, output_dict)))
    # future = asyncio.ensure_future(walk_elements(input_dict, output_dict))
    # responses = loop.run_until_complete(future)
    res = loop.run_until_complete(asyncio.gather(walk_elements(context, input_dict)))
    # nest_asyncio.apply(loop)
    loop.close()
    # from tackle.utils.dicts import nested_get2
    # x = nested_get2(input_dict, ('bar', 'bax', 'list', b'\x00\x00', 'this', 'that', b'\x00\x00', 'this', 'compact'))


nested_input = """
<-: var
this:
  <-: var
that:
  <-: var
foo:
    this:
      <-: var
    that:
      <-: var
bar:
  that:
    this:
      <-: var
    that:
      <-: var
  list:
    - this:
        that:
          - this:
              <-: var
          - that:
              <-: var
baz:
  lists:
    - <-: var
    - <-: var
    - <-: var
    - <-: var
"""


def test_async_walk_run_until_complete_yaml():
    loop = asyncio.get_event_loop()

    input_dict = yaml.safe_load(nested_input)
    output_dict = {}
    loop.run_until_complete(asyncio.gather(walk_elements(input_dict, output_dict)))
    loop.close()

    # assert ('foo', 'this') in output_dict


def test_is_tackle_hook():
    assert is_tackle_function('<-')
    assert is_tackle_function('<_')
    assert is_tackle_function('foo<-')
    assert is_tackle_function('foo<_')
    assert not is_tackle_function('<-foo')
    assert not is_tackle_function('<-foo')
