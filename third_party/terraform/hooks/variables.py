import logging
from typing import List

import hcl
from InquirerPy import prompt

from tackle import BaseHook, Context, Field, exceptions

logger = logging.getLogger(__name__)


class TerraformVariablesHook(BaseHook):
    """
    Hook that reads an input hcl file and prompts user to fill in any missing defaults
     similar to how terraform would do with missing vars.
    """

    hook_name: str = 'terraform_variables'

    var_list: List[str] = Field(
        None, description="List of specific variable names to be prompted for input."
    )
    var_skip_list: List[str] = Field(
        default_factory=list,
        description="List of variable names to be skipped during the prompting process.",
    )
    variables_file: str = Field(
        ..., description="Path to the Terraform variables file."
    )
    use_defaults: bool = Field(
        False,
        description="Flag to indicate whether to use default values for variables if "
        "available.",
    )

    def execute(self, context: Context) -> dict:
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
                    output = self._run_prompt(context, question, output, v)
        return output

    def _run_prompt(self, context: Context, question, output, v, var_type=None):
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
                    raise exceptions.HookCallException(
                        "Process has been cancelled by user.",
                        context=context,
                    )
            output.update({v: answer})
            return output
