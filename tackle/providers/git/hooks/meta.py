# -*- coding: utf-8 -*-

"""Meta hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import pathlib
import os
import re
from rich import print
import logging
import subprocess
from collections import MutableMapping
from PyInquirer import prompt

from pydantic import BaseModel, ValidationError
from tackle.utils.context_manager import work_in
from tackle.models import BaseHook
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class Repo(BaseModel):
    """Repo class for parsing dict inputs for repo."""

    src: str
    branch: Optional[str] = None
    tag: Optional[str] = None


# https://stackoverflow.com/a/6027615/12642712
def flatten_repo_tree(d, parent_key=''):
    """Flatten a dict to so that keys become nodes in a path."""
    items = []
    for k, v in d.items():
        new_key = os.path.join(parent_key, k)

        try:
            repo = Repo(**v)
        except (ValidationError, TypeError):
            repo = None

        if repo:
            items.append((new_key, v))
        elif isinstance(v, MutableMapping):
            # items.extend(flatten(v, new_key, sep=sep).items())
            items.extend(flatten_repo_tree(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)


class MetaGitHook(BaseHook):
    """Hook to create meta repo."""

    type: str = 'meta_repo'
    command: str = None

    repos: Dict = None
    repo_tree: Dict = None
    select: bool = True

    base_url: str = "https://github.com"
    git_org: str = None

    base_dir: str = os.path.abspath(os.path.curdir)
    meta_file: str = '.meta'

    def run_git_command(self, repo, folder_name, branch=None):
        """Run the git command."""
        if not branch:
            cmd = f"git {self.command} {repo} {folder_name}"
        else:
            cmd = f"git {self.command} {repo} {folder_name} -b {branch}"

        print()
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, err = p.communicate()
        if err:
            print(f"{err} for repo='{repo}' in folder='{folder_name}'.")

    def update_repo_name(self, v):
        """Update the repo name."""
        if re.compile(r"(https:\/\/[\w\.]+)|(git@[\w\.]+)").match(v):
            return v

        git_parts = v.split('/')
        if len(git_parts) == 1:
            if not self.git_org:
                print(
                    f"No git org declared - only one item declared in {v}, "
                    f"must be in form org/repo for abbreviated declarations. Skipping."
                )
                return
            else:
                return f"{self.base_url}/{self.git_org}/{git_parts[0]}"
        if len(git_parts) == 2:
            return f"{self.base_url}/{git_parts[0]}/{git_parts[1]}"
        else:
            print(f"Malformed repo name '{v}' in '{self.key}' key. Skipping.")

    def prompt_repo_choices(self):
        """Prompt the user to select which items to operate on."""
        choices = [{"name": "all repos"}] + [
            {"name": f"{k} --> {v}", "checked": True} for k, v in self.repo_tree.items()
        ]
        question = {
            'type': 'checkbox',
            'name': 'tmp',
            'message': f"Which repos do you want to {self.command.split(' ')[0]}?",
            'choices': choices,
        }
        repo_choices = prompt([question])['tmp']
        self.repo_tree = {
            k: v for k, v in self.repo_tree.items() if f"{k} --> {v}" in repo_choices
        }

    def get_command(self):
        """Get the git command to run."""
        if not self.no_input:
            git_commands = [
                '<custom input>',
                'clone',
                'pull',
                'branch',
            ]

            question = {
                'type': 'list',
                'name': 'tmp',
                'message': "What to do?",
                'choices': git_commands,
            }
            self.command = prompt([question])['tmp']

            # Extra input
            if self.command == '<custom input>':
                message = "Enter git command: "
                question = {
                    'type': 'input',
                    'name': 'tmp',
                    'message': message,
                }
                self.command = prompt([question])['tmp']
            if self.command == 'branch':
                message = "Enter git branch: "
                question = {
                    'type': 'input',
                    'name': 'tmp',
                    'message': message,
                }
                self.command = "branch " + prompt([question])['tmp']

        else:
            print(
                f"No command given in mete_hook for key = {self.key}.  "
                f"Defaults to clone."
            )
            self.command = 'clone'

    def execute(self):
        """Run the hook."""
        if not self.command:
            self.get_command()

        if self.repo_tree:
            self.repo_tree = flatten_repo_tree(self.repo_tree)

        if self.select and not self.no_input:
            self.prompt_repo_choices()

        for k, v in self.repo_tree.items():
            path, folder_name = os.path.split(k)
            if not os.path.isdir(path):
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)

            if isinstance(v, str):
                v = self.update_repo_name(v)
                if path != "":
                    with work_in(path):
                        self.run_git_command(v, folder_name)
                else:
                    self.run_git_command(v, folder_name)

            if isinstance(v, dict):
                r = Repo(**v)
                r.src = self.update_repo_name(r.src)
                if path != "":
                    with work_in(path):
                        self.run_git_command(r.src, folder_name, r.branch)
                else:
                    self.run_git_command(r.src, folder_name, r.branch)
