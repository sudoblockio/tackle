# -*- coding: utf-8 -*-
"""GCP hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from github import Github

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


def get_base():
    pass


class GithubReposHook(BaseHook):
    """Hook retrieving github repos.

    :param type: String hook type.
    :return: List of regions
    """

    type: str = 'github_repos'
    user: str = None
    password: str = None
    access_token: str = None
    base_url: str = None

    def execute(self):
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

        # for repo in g.get_user().get_repos():
        #     print(repo.name)
        # r = [r for r in g.get_user().get_repos()]
        for r in g.get_user().get_repos():
            x = r.name
        return g.get_user().get_repos()
