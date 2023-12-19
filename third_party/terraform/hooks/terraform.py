import shutil
from typing import Union

from python_terraform import Terraform

from tackle import Context, Field, exceptions
from tackle.models import BaseHook


class TerraformCmdHook(BaseHook):
    hook_name: str = 'terraform'

    cmd: str = Field(
        ...,
        description="The terraform command to run, ie init, plan, apply, destroy, "
        "output.",
    )
    targets: list = Field(
        None,
        description="List of specific resources to target. Used as default for "
        "apply/destroy/plan commands.",
    )
    state: str = Field(
        None,
        description="Path to the state file relative to the working directory. Used as "
        "default for apply/destroy/plan commands.",
    )
    variables: dict = Field(
        None,
        description="Default variables for apply/destroy/plan commands. Can be "
        "overridden by variables passed to the methods.",
    )
    parallelism: int = Field(
        None,
        description="Default parallelism level for apply/destroy commands.",
    )
    var_file: Union[list, str] = Field(
        None,
        description="Path to a variable file or a list of variable files. Passed as "
        "the -var-file option to Terraform.",
    )
    terraform_bin_path: str = Field(
        None,
        description="Path to the Terraform binary. If not specified, 'terraform' is "
        "used assuming it's in the system's PATH.",
    )
    is_env_vars_included: bool = Field(
        True,
        description="Indicates whether to include environment variables when calling "
        "Terraform commands.",
    )

    def execute(self, context: Context):
        if not shutil.which('terraform'):
            raise exceptions.HookCallException(
                "The terraform binary was not found in your path. Exiting...",
                context=context,
            )

        tf = Terraform(
            targets=self.targets,
            state=self.state,
            variables=self.variables,
            parallelism=self.parallelism,
            var_file=self.var_file,
            terraform_bin_path=self.terraform_bin_path,
            is_env_vars_included=self.is_env_vars_included,
        )
        command_methods = {
            'plan': tf.plan,
            'init': tf.init,
            'apply': tf.apply,
            'output': tf.output,
            'destroy': tf.destroy,
        }
        if self.cmd in command_methods:
            return_code, stdout, stderr = command_methods[self.cmd]()
            if return_code != 0:
                raise exceptions.HookCallException(
                    f"Terraform {self.cmd} command failed with exit code "
                    f"{return_code}. Stderr: {stderr}",
                    context=context,
                )
            return stdout
        else:
            raise exceptions.HookCallException(
                f"Unsupported Terraform command: {self.cmd}",
                context=context,
            )
