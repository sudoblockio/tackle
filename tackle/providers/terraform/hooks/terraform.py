# -*- coding: utf-8 -*-

"""Terraform hooks."""
from __future__ import print_function
from __future__ import unicode_literals

import logging
from typing import List

import hcl
from PyInquirer import prompt
from pydantic import FilePath

from tackle.exceptions import EscapeHookException
from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class TerraformVariablesHook(BaseHook):
    """
    Hook that reads an input hcl file and prompts user to fill in.

    Typically this is used with a `variables.tf` file.

    :param variables_file: A path to a file to read
    :param var_list: A list of items to only parse and prompt
    :param var_skip_list: A list of items to skip when prompting

    :return: Dictionary that can be dumped into json for a `terraform.tfvars.json`
    """

    type: str = 'terraform_variables'

    var_list: List[str] = None
    var_skip_list: List[str] = []
    variables_file: FilePath

    def execute(self):
        with open(self.variables_file, 'r') as f:
            vars = hcl.load(f)

        output = {}
        for v in vars['variable'].keys() if not self.var_list else self.var_list:
            logger.debug('Parsing %s variable', v)

            var = vars['variable'][v]

            description = (
                f"\nDescription - {var['description']}" if 'description' in var else ""
            )
            message = f'What do you want to set the variable "{v}" {description}'

            if 'type' in var:
                if var['type'] in ['bool', 'boolean'] and v not in self.var_skip_list:
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'confirm',
                        'default': var['default'] if 'default' in var else True,
                        'message': message,
                        'name': v,
                    }
                    output = self._run_prompt(question, output, v)

                if var['type'] in ['string'] and v not in self.var_skip_list:
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'input',
                        'default': var['default'] if 'default' in var else None,
                        'message': message,
                        'name': v,
                    }
                    output = self._run_prompt(question, output, v)

                if (
                    var['type'] in ['list', 'list(string)', 'list(map(string))']
                    and v not in self.var_skip_list
                ):
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'checkbox',
                        'default': var['default'] if 'default' in var else None,
                        'message': message,
                        'choices': '',
                        'name': v,
                    }
                    logger.debug('Variable type %s', var['type'])

                    output = self._run_prompt(question, output, v)

                if (
                    var['type'] in ['map', 'map(string)']
                    and v not in self.var_skip_list
                ):
                    logger.debug('Variable type %s', var['type'])
                    question = {
                        'type': 'checkbox',
                        'default': var['default'] if 'default' in var else None,
                        'message': message,
                        'name': v,
                    }
                    output = self._run_prompt(question, output, v)

        return output

    @staticmethod
    def _run_prompt(question, output, v, var_type=None):
        question.update({'name': 'tmp'})
        answer = prompt([question])['tmp']
        if not isinstance(var_type, dict):
            if answer == {}:
                raise EscapeHookException("Process has been cancelled by user.")
        output.update({v: answer})
        return output
