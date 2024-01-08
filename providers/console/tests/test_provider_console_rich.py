from tackle.main import tackle
from tackle.utils.hooks import get_hook


def test_provider_system_hook_rich_table():
    output = tackle('table.yaml', no_input=True)
    assert 'table' in output


def test_provider_system_hook_rich_table_split():
    output = tackle('table_split.yaml', no_input=True)
    assert 'table_split' in output


def test_provider_console_markdown():
    output = tackle('markdown.yaml')
    assert output['md']


def test_provider_console_markdown_frontmatter():
    Hook = get_hook('markdown_frontmatter')
    output = Hook(path='frontmatter.md').exec()

    assert output['foo'] == 'bar'
    assert len(output['stuff']) == 1


def test_provider_console_markdown_frontmatter_none():
    """Check that an empty dict returns when there is no frontmatter."""
    Hook = get_hook('markdown_frontmatter')
    output = Hook(path='frontmatter-none.md').exec()

    assert output == {}
