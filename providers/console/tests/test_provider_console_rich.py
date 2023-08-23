"""Tests dict input objects for `tackle.providers.rich.hooks.table` module."""
from tackle.main import tackle


def test_provider_system_hook_rich_table(change_dir):
    output = tackle('table.yaml', no_input=True)
    assert 'table' in output


def test_provider_system_hook_rich_table_split(change_dir):
    output = tackle('table_split.yaml', no_input=True)
    assert 'table_split' in output


def test_provider_console_markdown(change_dir):
    output = tackle('markdown.yaml')
    assert output['md']
