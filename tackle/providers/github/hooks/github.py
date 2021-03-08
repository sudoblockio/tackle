# -*- coding: utf-8 -*-
"""Github hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from github import Github
from typing import Any
from tackle.models import BaseHook
from tackle.exceptions import HookCallException

logger = logging.getLogger(__name__)


class GithubBaseHook(BaseHook):
    """Hook retrieving github repos.

    :param type: String hook type.
    :return: List of regions
    """

    type = "NULL"
    user: str = None
    org: str = None
    password: str = None
    access_token: str = None
    base_url: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.org and self.user:
            raise HookCallException("Can't specify both user and org in github hook.")
        # Default to using org as the top level
        self.org = self.user

    def get_github_client(self):
        """Get github client base method."""
        if self.user and self.password:
            # using username and password
            g = Github(self.user, self.password)
        elif self.access_token:
            # or using an access token
            g = Github(self.access_token)
        elif self.base_url and self.access_token:
            # Github Enterprise with custom hostname
            g = Github(base_url=self.base_url, login_or_token=self.access_token)
        else:
            g = Github()
        return g


class GithubRepoHook(GithubBaseHook, BaseHook):
    """Hook retrieving github repo names.

    :param type: String hook type.
    :return: List of regions
    """

    type: str = 'github_repo_names'

    def execute(self):
        """Run the hook."""
        g = self.get_github_client()
        return [r.name for r in g.get_user(self.org).get_repos()]


class GithubRepoReleasesHook(GithubBaseHook, BaseHook):
    """Hook retrieving github repo releases.

    :param type: String hook type.
    :return: List of versions
    """

    type: str = 'github_repo_releases'
    repo: str

    def execute(self):
        """Run the hook."""
        g = self.get_github_client()
        repo = g.get_repo(f"{self.org}/{self.repo}")
        return [r.tag_name for r in repo.get_releases()]
