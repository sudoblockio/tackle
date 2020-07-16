# -*- coding: utf-8 -*-

"""Operator plugin base class that all __subclassess__ are brought in scope."""
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from os import listdir as _listdir  # To not conflict with operator
from os.path import dirname, basename, join, isdir
from cookiecutter.context_manager import work_in

# TODO: Allow for imports of custom operators and subdirectories.
__all__ = [
    basename(f)[:-3]
    for f in _listdir(dirname(__file__))
    if f[-3:] == ".py" and not f.endswith("__init__.py")
]


class BaseOperator(metaclass=ABCMeta):
    """Base operator mixin class."""

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize BaseOperator."""
        self.operator_dict = operator_dict
        self.context = context or {}
        self.context_key = context_key or 'cookiecutter'
        self.no_input = no_input
        self.post_gen_operator = False

        self.chdir = (
            self.operator_dict['chdir'] if 'chdir' in self.operator_dict else None
        )

    @abstractmethod
    def execute(self):
        """Run the operator."""
        raise NotImplementedError()

    def _execute(self):
        if self.chdir and isdir(self.chdir):
            # Use contextlib to switch dirs and come back out
            with work_in(self.chdir):
                return self.execute()
        elif self.chdir:
            # This makes no sense really but it was working then broke so above
            # is fix, leave this but should remove. Works when given relative path
            # But so does above...
            template_dir = self.context[self.context_key]['_template']
            target_dir = join(template_dir, self.chdir)
            with work_in(target_dir):
                return self.execute()
        else:
            return self.execute()
