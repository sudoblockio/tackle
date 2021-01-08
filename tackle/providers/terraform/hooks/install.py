# -*- coding: utf-8 -*-

"""Terraform hooks."""
from __future__ import print_function
from __future__ import unicode_literals

import logging
import stat
import os
import re
import platform as _platform
from PyInquirer import prompt
import requests
import zipfile
import tempfile
import shutil

from tackle.utils.context_manager import work_in
from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class TerraformVersionsHook(BaseHook):
    """
    Hook that reads an input hcl file and prompts user to fill in.
    :param :
    :return:
    """

    type: str = 'terraform_version'
    minor_version: str = None
    patch_version: str = None

    def execute(self):
        response = requests.get("https://releases.hashicorp.com/terraform/")
        versions = []
        for l in response.text.split('\n'):
            match = re.search("\/(\d+\.\d+\.\d+)(-[a-zA-z]+\d*)?\/", l)  # noqa
            if match:
                versions.append(match.group(1))

        if self.minor_version:
            versions = [v for v in versions if v.split('.')[1] == self.minor_version]

        return versions


class TerraformInstallHook(BaseHook):
    """
    Hook that reads an input hcl file and prompts user to fill in.
    :param :
    :return:
    """

    type: str = 'terraform_install'

    output_dir: str = os.path.abspath(os.curdir)
    output_file_name: str = "terraform"
    version: str = "0.13.6"

    platform: str = None
    platform_choose: bool = False

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


# https://releases.hashicorp.com/terraform/0.13.6/terraform_0.13.6_linux_amd64.zip
# https://releases.hashicorp.com/terraform/0.13.6/terraform_0.13.6_linux-amd64.zip
# https://releases.hashicorp.com/terraform/0.13.6/terraform_0.13.6_linux-amd64.zip
# https://releases.hashicorp.com/terraform/0.13.6/terraform_0.13.6_linux_amd64.zip
