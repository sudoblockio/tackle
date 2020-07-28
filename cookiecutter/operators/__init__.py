# -*- coding: utf-8 -*-

"""Operator plugin base class that all __subclassess__ are brought in scope."""
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from os import listdir as _listdir  # To not conflict with operator
from os.path import dirname, basename, join, isdir, abspath, expanduser
from cookiecutter.context_manager import work_in

# TODO: Allow for imports of custom operators and subdirectories.
__all__ = [
    basename(f)[:-3]
    for f in _listdir(dirname(__file__))
    if f[-3:] == ".py" and not f.endswith("__init__.py")
]


class BaseOperator(metaclass=ABCMeta):
    """Base operator mixin class."""

    def __init__(
        self, operator_dict=None, context=None, context_key=None, no_input=False
    ):
        """
        Initialize BaseOperator.

        :param operator_dict: A dictionary of the operator that is already rendered
            and has kwargs for the specific operator.
        :param context: The entire context of the operator.
        :param context_key: The key for the context - defaults to filename without
            extension
        :param no_input: Boolean to indicate whether to prompt the user for anything
        :param post_gen_operator: Boolean to indiciate if to run the operator after
            all the other operators.
        :param chdir: A directory to temporarily change directories into and execute
             the operator.
        """
        self.operator_dict = operator_dict
        self.context_key = context_key or 'cookiecutter'
        self.context = context or {}

        if 'no_input' in self.operator_dict:
            self.no_input = self.operator_dict['no_input']
        else:
            self.no_input = no_input

        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )
        self.chdir = (
            self.operator_dict['chdir'] if 'chdir' in self.operator_dict else None
        )

    @abstractmethod
    def _execute(self):
        raise NotImplementedError()

    def execute(self):
        """
        Execute the `_execute` method within each operator.

        Handles `chdir` method.
        """
        if self.chdir and isdir(abspath(expanduser(self.chdir))):
            # Use contextlib to switch dirs and come back out
            with work_in(abspath(expanduser(self.chdir))):
                return self._execute()
        elif self.chdir:
            # This makes no sense really but it was working then broke so above
            # is fix, leave this but should remove. Works when given relative path
            # But so does above...
            template_dir = self.context[self.context_key]['_template']
            target_dir = join(template_dir, self.chdir)
            with work_in(target_dir):
                return self._execute()
        else:
            return self._execute()
