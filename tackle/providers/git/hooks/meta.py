import pathlib
import os
import re
import subprocess
from collections.abc import MutableMapping

from InquirerPy import prompt
from InquirerPy.base.control import Choice

from pydantic import BaseModel, ValidationError, validator
from typing import Optional

from tackle.utils.paths import work_in
from tackle.models import BaseHook, Field


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
            items.extend(flatten_repo_tree(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)


class MetaGitHook(BaseHook):
    """
    Hook to create meta repo, ie a repo that has many other repos within it. See
     [meta repo definition.](https://notes.burke.libbey.me/metarepo/#:~:text=a%20%E2%80%9CMetarepo%E2%80%9D.-,Metarepo%20Architecture,branch%20commit%20for%20each%20repository.)
     Describe the repo structure with a map and when this hook is called, it allows the
     users to operate git commands on that repo structure.
    """

    __slots__ = ('first_run',)
    # Per https://github.com/samuelcolvin/pydantic/issues/655 for private vars

    hook_type: str = 'meta_repo'
    command: str = Field(None, description="The git command to run.")
    repo_tree: dict = Field(
        None,
        description="A map of repos to clone with the keys indicating the path "
        "and values for the repo targets. See examples.",
    )
    protocol: str = Field(
        "https",
        description="Either https or ssh. Useful when using abbreviated repo "
        "references.",
    )
    token: str = Field(
        None, description="A token to use with https abbreviated repo references."
    )
    base_url: str = Field(
        "github.com",
        description="The base url to use with https abbreviated repo " "references.",
    )
    git_org: str = Field(
        None,
        description="The git org to override with https abbreviated repo "
        "references.",
    )

    _doc_tags: list = ["experimental"]
    _issue_numbers: list = []

    @validator('token')
    def no_token_with_ssh_protocol(cls, v, values, **kwargs):
        if v and values['protocol'] == 'ssh':
            raise ValueError("Can't supply token with ssh protocol.")
        else:
            return v

    @validator('base_url')
    def update_base_url_if_token_exists(cls, v, values, **kwargs):
        if values['token']:
            return values['token'] + ':x-oauth-basic@' + v
        else:
            return v

    def get_repo_prefix(self, repo):
        """Return a string to prefix url."""
        if repo.startswith("https") or repo.startswith("git"):
            # Case where it is provided
            return ""
        if self.protocol == "https":
            return f"https://{self.base_url}/"
        if self.protocol == "ssh":
            return f"git@{self.base_url}:"

    def get_git_command(self, branch, repo, folder_name):
        """Build string to run git command."""
        if self.command == 'clone':
            if not branch:
                return f"git {self.command} {self.get_repo_prefix(repo)}{repo} {folder_name}"
            else:
                return (
                    f"git {self.command} {self.get_repo_prefix(repo)}{repo} "
                    f"{folder_name} -b {branch}"
                )
        elif self.command == 'pull':
            return f"git {self.command}"

        # if not branch:
        #     return (
        #         f"git {self.command} {self.get_repo_prefix(repo)}{repo} {folder_name}"
        #     )
        # else:
        #     return (
        #         f"git {self.command} {self.get_repo_prefix(repo)}{repo} "
        #         f"{folder_name} -b {branch}"
        #     )

    def execute_git_command(self, branch, repo, folder_name):
        """Execute the git command."""
        cmd = self.get_git_command(branch, repo, folder_name)
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, err = p.communicate()

        if err:
            print(f"{err} for repo='{repo}' in folder='{folder_name}'.")

    def try_https_then_ssh(self, branch, repo, folder_name):
        """When running first git command, tries with https then falls back to ssh."""
        try:
            self.execute_git_command(branch, repo, folder_name)
            object.__setattr__(self, 'first_run', False)
        except Exception:
            try:
                self.protocol = "ssh"
                self.execute_git_command(branch, repo, folder_name)
            except Exception as e:
                print(f"{e} for repo='{repo}' - Neither https or ssh works. Skipping.")

    def run_git_command(self, repo, folder_name, branch=None):
        """Run the git command."""
        if self.first_run:
            self.try_https_then_ssh(branch, repo, folder_name)
        self.execute_git_command(branch, repo, folder_name)

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
                return f"{self.git_org}/{git_parts[0]}"
        if len(git_parts) == 2:
            return f"{git_parts[0]}/{git_parts[1]}"
        else:
            from tackle.utils.dicts import get_key_from_key_path

            key = get_key_from_key_path(self.key_path)
            print(f"Malformed repo name '{v}' in '{key}' key. Skipping.")

    def prompt_repo_choices(self):
        """Prompt the user to select which items to operate on."""
        choices = [
            Choice({k: v}, name=f"{k} --> {v}", enabled=True)
            for k, v in self.repo_tree.items()
        ]
        question = {
            'type': 'checkbox',
            'name': 'tmp',
            'message': f"Which repos do you want to {self.command.split(' ')[0]}?",
            'choices': choices,
        }
        repo_choices = prompt([question])['tmp']
        # Return a single dict with all the k/v in one
        self.repo_tree = {list(i.keys())[0]: list(i.values())[0] for i in repo_choices}

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
            # print(
            #     f"No command given in mete_hook for key = {self.key}.  "
            #     f"Defaults to clone."
            # )
            self.command = 'clone'

    def exec(self):
        """Run the hook."""
        object.__setattr__(self, 'first_run', True)

        if not self.command:
            self.get_command()

        # Flatten the repo tree = `{k1: {k2: v}}` -> `[{k1/k2: v}]` where `k1/k2`
        # is the path to operate (ie clone, etc) on the repo object `v` that can be
        # a string or dict
        if self.repo_tree:
            self.repo_tree = flatten_repo_tree(self.repo_tree)

        # Select is a bool that can override whether to prompt
        if not self.no_input:
            self.prompt_repo_choices()

        # Parse flattened repo tree from above
        for k, v in self.repo_tree.items():
            # Create dir to base path if it does not exist
            path, folder_name = os.path.split(k)
            if not os.path.isdir(path):
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)

            # Handle string inputs
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
