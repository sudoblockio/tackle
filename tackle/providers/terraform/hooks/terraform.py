# -*- coding: utf-8 -*-

"""Terraform hooks."""
from __future__ import print_function
from __future__ import unicode_literals

import logging
from typing import List

import hcl
from PyInquirer import prompt
from pydantic import FilePath
from pydantic import BaseModel, validator, root_validator
from typing import Union
from python_terraform import *
from tackle.exceptions import HookCallException
from shutil import which


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
    variables_file: str
    use_defaults: bool = False

    def execute(self) -> dict:
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

    def _run_prompt(self, question, output, v, var_type=None):
        if v in self.overwrite_inputs:
            output.update({v: self.overwrite_inputs[v]})
            return output

        if self.no_input or self.use_defaults:
            output.update({v: question['default']})
            return output
        else:
            question.update({'name': 'tmp'})
            answer = prompt([question])['tmp']
            if not isinstance(var_type, dict):
                if answer == {}:
                    raise EscapeHookException("Process has been cancelled by user.")
            output.update({v: answer})
            return output


class TerraformMixin(BaseModel):
    targets: list = None
    state: str = None
    variables: dict = None
    parallelism: int = None
    var_file: Union[list, str] = None
    terraform_bin_path: str = 'terraform' # "/home/rob/bin/terraform" #
    is_env_vars_included: bool = True


TERRAFORM_CMDS = [
    "init",
    "plan",
    "apply",
    "output",
    "destroy",
    "import",
]

class TerraformCmdHook(BaseHook, TerraformMixin):
    type: str = 'terraform'
    cmd: str

    @validator('cmd')
    def cmd_must_be_in_list(cls, v):
        if v not in TERRAFORM_CMDS:
            raise HookCallException(f'Terraform `cmd` must be one of {", ".join(TERRAFORM_CMDS)}.')
        return v

    # @root_validator('terraform_bin_path')
    # def update_executable_to_full_path(cls, v):
    #     return which(v)

    def execute(self):
        # self.terraform_bin_path = which(self.terraform_bin_path)
        # y = self.terraform_bin_path
        # x = which(b"{self.terraform_bin_path}")

        import shutil
        import sys
        s = shutil.which("terraform")
        ff = sys.path
        tf = Terraform(**{k: v for k, v in self.dict().items() if k in TerraformMixin().dict().keys()})
        f = os.environ["PATH"]

        if self.cmd == 'plan':
            return_code, stdout, stderr = tf.plan()
        if self.cmd == 'init':
            return_code, stdout, stderr = tf.init()
        if self.cmd == 'apply':
            return_code, stdout, stderr = tf.apply()
        if self.cmd == 'output':
            return_code, stdout, stderr = tf.output()
        if self.cmd == 'destroy':
            return_code, stdout, stderr = tf.destroy()
        if self.cmd == 'plan':
            return_code, stdout, stderr = tf.plan()
