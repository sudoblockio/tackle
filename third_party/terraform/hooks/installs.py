import logging
import os
import platform as _platform
import re
import shutil
import stat
import tempfile
import zipfile

import requests
from InquirerPy import prompt

from tackle import BaseHook, Field
from tackle.utils.paths import work_in

logger = logging.getLogger(__name__)


class TerraformVersionsHook(BaseHook):
    """Hook that returns a list of terraform versions based off criteria."""

    hook_name: str = 'terraform_version'
    minor_version: str = None
    patch_version: str = None

    def execute(self) -> list:
        response = requests.get("https://releases.hashicorp.com/terraform/")
        versions = []
        for line in response.text.split('\n'):
            match = re.search(r"\/(\d+\.\d+\.\d+)(-[a-zA-z]+\d*)?\/", line)
            if match:
                versions.append(match.group(1))

        if self.minor_version:
            versions = [v for v in versions if v.split('.')[1] == self.minor_version]

        return versions


class TerraformInstallHook(BaseHook):
    """Hook that installs terraform into a specific directory."""

    hook_name: str = 'terraform_install'

    output_dir: str = Field(
        default_factory=lambda: os.path.abspath(os.curdir),
        description="Path to the directory where Terraform will be installed.",
    )
    output_file_name: str = Field(
        default="terraform", description="Name of the Terraform executable file."
    )
    version: str = Field(
        default="0.13.6", description="The version of Terraform to install."
    )
    platform: str | None = Field(
        default=None,
        description="The platform for which to download Terraform. If not specified, "
        "it will be inferred.",
    )
    platform_choose: bool = Field(
        default=False,
        description="Flag to indicate whether to prompt the user for platform choice.",
    )

    @staticmethod
    def _get_procesor():
        if 'x86' in _platform.processor():
            return 'amd64'
        if '386' in _platform.processor():
            return '386'
        if 'arm' in _platform.processor():
            return 'arm'
        raise ValueError("Don't know what type of processor you are using.")

    def _get_platform(self):
        platforms = [
            'darwin_amd64',
            'freebsd_386',
            'freebsd_amd64',
            'freebsd_arm',
            'linux_386',
            'linux_amd64',
            'linux_arm',
            'openbsd_386',
            'openbsd_amd64',
            'solaris_amd64',
            'windows_386',
            'windows_amd64',
        ]

        if self.platform:
            pass

        processor = self._get_procesor()

        if _platform.system() == 'Linux':
            self.platform = '_'.join(['linux', processor])
        elif _platform.system() == 'Windows':
            self.platform = '_'.join(['windows', processor])
        elif _platform.system() == 'Darwin':
            self.platform = '_'.join(['darwin', processor])

        if self.platform_choose:
            question = {
                'type': 'list',
                'name': 'tmp',
                'message': "Which platform are you on?",
                'default': self.platform,
                'choices': platforms,
            }
            self.platform = prompt([question])['tmp']
            if self.platform not in platforms:
                raise ValueError("Logic is broken to detect platrform. Fix ME!")

    def execute(self):
        self._get_platform()
        url = f"https://releases.hashicorp.com/terraform/{self.version}/terraform_{self.version}_{self.platform}.zip"
        local_filename = url.split('/')[-1]
        # if not self.output_dir:
        #     self.output_dir = os.path.abspath(os.curdir)

        download_path = os.path.join(tempfile.gettempdir(), local_filename)
        if not os.path.isfile(download_path):
            with work_in(tempfile.gettempdir()):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    raise SystemExit(err)

                if response.status_code == 200:
                    with open(local_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
        # Unzip the file in the tmp directory
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(tempfile.gettempdir())

        # Move the file from the tmp directory
        output_path = os.path.join(self.output_dir, self.output_file_name)
        shutil.move(os.path.join(tempfile.gettempdir(), "terraform"), output_path)

        # Activate the file
        st = os.stat(output_path)
        os.chmod(output_path, st.st_mode | stat.S_IEXEC)

        return self.output_dir


class TerragruntInstallHook(BaseHook):
    """Hook that installs terragrunt into a specific directory."""

    hook_name: str = 'terragrunt_install'

    output_dir: str = Field(
        default_factory=lambda: os.path.abspath(os.curdir),
        description="Path to the directory where Terragrunt will be installed.",
    )
    output_file_name: str = Field(
        default="terragrunt", description="Name of the Terragrunt executable file."
    )
    version: str = Field(
        default="v0.27.3", description="The version of Terragrunt to install."
    )
    platform: str | None = Field(
        default=None,
        description="The platform for which to download Terragrunt. If not specified, it will be inferred.",
    )
    platform_choose: bool = Field(
        default=False,
        description="Flag to indicate whether to prompt the user for platform choice.",
    )

    @staticmethod
    def _get_procesor():
        if 'x86' in _platform.processor():
            return 'amd64'
        if '386' in _platform.processor():
            return '386'
        raise ValueError("Don't know what type of processor you are using.")

    def _get_platform(self):
        platforms = [
            'darwin_amd64',
            'darwin_386',
            'linux_386',
            'linux_amd64',
            'windows_386',
            'windows_amd64',
        ]

        if self.platform:
            pass

        processor = self._get_procesor()

        if _platform.system() == 'Linux':
            self.platform = '_'.join(['linux', processor])
        elif _platform.system() == 'Windows':
            self.platform = '_'.join(['windows', processor])
        elif _platform.system() == 'Darwin':
            self.platform = '_'.join(['darwin', processor])

        if self.platform_choose:
            question = {
                'type': 'list',
                'name': 'tmp',
                'message': "Which platform are you on?",
                'default': self.platform,
                'choices': platforms,
            }
            self.platform = prompt([question])['tmp']
            if self.platform not in platforms:
                raise ValueError("Logic is broken to detect platrform. Fix ME!")

    def execute(self):
        self._get_platform()
        url = f"https://github.com/gruntwork-io/terragrunt/releases/download/{self.version}/terragrunt_{self.platform}"
        local_filename = url.split('/')[-1]
        # if not self.output_dir:
        #     self.output_dir = os.path.abspath(os.curdir)

        download_path = os.path.join(tempfile.gettempdir(), local_filename)
        if not os.path.isfile(download_path):
            with work_in(tempfile.gettempdir()):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    raise SystemExit(err)

                if response.status_code == 200:
                    with open(local_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
        # # Unzip the file in the tmp directory
        # with zipfile.ZipFile(download_path, 'r') as zip_ref:
        #     zip_ref.extractall(tempfile.gettempdir())

        # Move the file from the tmp directory
        output_path = os.path.join(self.output_dir, self.output_file_name)
        shutil.move(download_path, output_path)

        # Activate the file
        st = os.stat(output_path)
        os.chmod(output_path, st.st_mode | stat.S_IEXEC)

        return self.output_dir
