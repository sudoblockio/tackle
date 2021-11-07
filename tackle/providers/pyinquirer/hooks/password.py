# -*- coding: utf-8 -*-

"""Password hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt
from typing import Any
from pydantic import Field

from tackle.models import BaseHook
from tackle.utils import literal_type

logger = logging.getLogger(__name__)


class InquirerPasswordHook(BaseHook):
    """
    Hook for PyInquirer `password` type prompts.

    :param message:
    :param choices: A list of strings or list of k/v pairs per above description
    :param name: A key to insert the output value to. If not provided defaults to
        inserting into parent key
    :return:
    """

    type: str = 'password'

    default: Any = Field(None, description="Default choice.")
    message: str = Field(None, description="String message to show when prompting.")
    name: str = Field('tmp', description="Extra key to embed into. Artifact of API.")

    _args: list = ['message', 'default']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.message:
            self.message = ''.join([self.key, " >> "])

    def execute(self) -> bool:
        if not self.no_input:
            question = {
                'type': self.type,
                'name': self.name,
                'message': self.message,
                'default': self.default,
            }

            response = prompt([question])
            if self.name != 'tmp':
                return response
            else:
                return response['tmp']
        elif self.default:
            return self.default
        else:
            # When no_input then return empty list
            return True
