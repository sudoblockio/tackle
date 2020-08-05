# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from rich.console import Console
from rich.table import Table

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class TableOperator(BaseOperator):
    """
    Operator for creating tables with rich - github.com/willmcgugan/rich.

    :param column_names: List of column names
    :param contents: List of lists to put into columns / rows
    :param contents_split: List of strings to separate into columns based on `separator`
    :param separator: A string to separate the strings in the contents
    :param sort: Boolean to sort contents or contents_split
    """

    type = 'table'

    def __init__(self, *args, **kwargs):  # noqa
        super(TableOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        if self.operator_dict['sort'] if 'sort' in self.operator_dict else False:
            if 'contents' in self.operator_dict:
                self.operator_dict['contents'].sort()
            if 'contents_split' in self.operator_dict:
                self.operator_dict['contents_split'].sort()

        console = Console()

        self.operator_dict['column_names'] = (
            self.operator_dict['column_names']
            if 'column_names' in self.operator_dict
            else []
        )
        if len(self.operator_dict['column_names']) > 0:
            table = Table(show_header=True, header_style="bold red")
            for c in self.operator_dict['column_names']:
                table.add_column(c)
        else:
            table = Table()

        if 'contents_split' in self.operator_dict:
            for i in self.operator_dict['contents_split']:
                table.add_row(
                    *i.split(self.operator_dict['separator'])[
                        0 : len(self.operator_dict['column_names'])  # noqa
                    ]
                )

        if 'contents' in self.operator_dict:
            for i in self.operator_dict['contents']:
                table.add_row(*set(i))

        console.print(table)
