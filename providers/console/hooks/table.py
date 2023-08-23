from rich.console import Console
from rich.table import Table
from typing import List, Any

from tackle.models import BaseHook, Field


class TableHook(BaseHook):
    """Hook for creating tables with rich - github.com/willmcgugan/rich."""

    hook_type: str = 'table'

    column_names: List = Field([], description="List of column names")
    sort: bool = Field(False, description="Boolean to sort contents or contents_split")
    contents: Any = Field(None, description="List of lists to put into columns / rows")
    contents_split: List = Field(
        None,
        description="List of strings to separate into columns based on `separator`",
    )
    separator: str = Field(
        None, description="A string to separate the strings in the contents"
    )

    def exec(self):
        if self.sort:
            if self.contents:
                self.contents.sort()
            if self.contents_split:
                self.contents_split.sort()

        console = Console()

        if len(self.column_names) > 0:
            table = Table(show_header=True, header_style="bold red")
            for c in self.column_names:
                table.add_column(c)
        else:
            table = Table()

        if self.contents_split:
            for i in self.contents_split:
                table.add_row(
                    *i.split(self.separator)[0 : len(self.column_names)]  # noqa
                )

        if self.contents:
            for i in self.contents:
                table.add_row(*[str(j) for j in i])

        console.print(table)
