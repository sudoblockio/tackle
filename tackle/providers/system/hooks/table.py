# -*- coding: utf-8 -*-

"""Table hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from rich.console import Console
from rich.table import Table
from typing import List, Any

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class TableHook(BaseHook):
    """
    Hook  for creating tables with rich - github.com/willmcgugan/rich.

    :param column_names: List of column names
    :param contents: List of lists to put into columns / rows
    :param contents_split: List of strings to separate into columns based on `separator`
    :param separator: A string to separate the strings in the contents
    :param sort: Boolean to sort contents or contents_split
    """

    type: str = 'table'

    column_names: List = []
    sort: bool = False
    contents: Any = None
    contents_split: List = None
    # TODO: Validate one of above is entered
    separator: str = None

    def execute(self):
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
