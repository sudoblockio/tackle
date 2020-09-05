# -*- coding: utf-8 -*-

"""Operator plugin base class that all __subclassess__ are brought in scope."""
from __future__ import unicode_literals

import logging
from os import listdir as _listdir  # To not conflict with operator
from os.path import dirname, basename, join, isdir, abspath, expanduser
from PyInquirer import prompt
from pydantic import BaseModel
from typing import Dict, Optional, Any


import cookiecutter as cc
from cookiecutter.context_manager import work_in

logger = logging.getLogger(__name__)

# TODO: Allow for imports of custom operators and subdirectories.
__all__ = [
    basename(f)[:-3]
    for f in _listdir(dirname(__file__))
    if f[-3:] == ".py" and not f.endswith("__init__.py")
]


class BaseOperator(BaseModel):
    """Base operator mixin class."""

    context: Dict = None
    context_key: str = None
    no_input: bool = None
    cc_dict: Dict = None
    env: Any = None
    key: str = None

    chdir: Optional[str] = None
    post_gen_operator: Optional[bool] = False
    confirm: Optional[str] = False
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
    :param confirm:
    """

    class Config:
        arbitrary_types_allowed = True

    def execute(self):
        """Abstract method."""
        raise NotImplementedError()

    def call(self) -> None:
        """
        Call main entrypoint to calling operator.

        Handles `chdir` method.
        """
        if self.chdir and isdir(abspath(expanduser(self.chdir))):
            # Use contextlib to switch dirs and come back out
            with work_in(abspath(expanduser(self.chdir))):
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

    def _evaluate_confirm(self):
        if self.confirm:
            if isinstance(self.confirm, str):
                return prompt(
                    [{'type': 'confirm', 'name': 'tmp', 'message': self.confirm}]
                )['tmp']
            elif isinstance(self.confirm, dict):
                if 'when' in self.confirm:
                    when_condition = cc.operator.evaluate_when(
                        self.operator_dict,  # noqa
                        self.env,
                        self.cc_dict,
                        self.context_key,
                    )
                    if when_condition:
                        return prompt(
                            [
                                {
                                    'type': 'confirm',
                                    'name': 'tmp',
                                    'message': self.confirm['message'],
                                    'default': self.confirm['default'],
                                }
                            ]
                        )['tmp']
