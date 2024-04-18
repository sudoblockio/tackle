from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from ruyaml import YAML

from tackle import BaseHook, Field


class MarkdownPrintHook(BaseHook):
    """Hook for printing markdown and returning the output."""

    hook_name = 'markdown'
    text: str = Field(..., description="The text to render as markdown.")
    justify: str = Field(
        None, description="Justify value for paragraphs. Defaults to None."
    )

    args: list = ['text']

    # TODO: Map this https://rich.readthedocs.io/en/stable/reference/markdown.html?highlight=markdown%20#rich.markdown.Markdown
    # https://github.com/sudoblockio/tackle/issues/57
    def exec(self):
        console = Console()
        console.print(Markdown(self.text, justify='left', inline_code_lexer='python'))
        return self.text


class MarkdownFrontmatterHook(BaseHook):
    """Hook for reading frontmatter from a Markdown file."""

    hook_name = 'markdown_frontmatter'
    path: str = Field(..., description="Path to the Markdown file.")

    args: list = ['path']

    def exec(self) -> Optional[dict]:
        with open(self.path, 'r') as file:
            lines = file.readlines()

        # Find the start and end of the frontmatter
        if lines[0].strip() == '---':
            end = 1
            while end < len(lines) and lines[end].strip() != '---':
                end += 1

            # Parse the frontmatter
            frontmatter = ''.join(lines[1:end])
            yaml = YAML()
            return dict(yaml.load(frontmatter))

        return {}
