# -*- coding: utf-8 -*-

"""Meta hooks."""
from __future__ import unicode_literals
from __future__ import print_function

from git import Repo
import logging
from tackle.models import BaseHook
from typing import Optional

logger = logging.getLogger(__name__)


class GitCloneHook(BaseHook):
    """
    Hook to create clone a repo.

    Wraps https://gitpython.readthedocs.io/en/stable/reference.html#git.repo.base.Repo.clone

    :param url: – valid git url, see
        http://www.kernel.org/pub/software/scm/git/docs/git-clone.html#URLS
    :param to_path: – Path to which the repository should be cloned to
    :param progress: – See ‘git.remote.Remote.push’.
    :param env: – Optional dictionary containing the desired environment variables.
        Note: Provided variables will be used to update the execution environment for git.
        If some variable is not specified in env and is defined in os.environ, value from
        os.environ will be used. If you want to unset some variable, consider providing empty
        string as its value.
    :param path: – is the full path of the new repo (traditionally ends with ./<name>.git).
    :param progress: – See ‘git.remote.Remote.push’.
    :param multi_options: – A list of Clone options that can be provided multiple times. One
        option per list item which is passed exactly as specified to clone. For example
        [‘–config core.filemode=false’, ‘–config core.ignorecase’, ‘–recurse-submodule=repo1_path’,
        ‘–recurse-submodule=repo2_path’]
    :param kwargs: –
            odbt = ObjectDatabase Type, allowing to determine the object database implementation
                used by the returned Repo instance
            All remaining keyword arguments are given to the git-clone command
    """

    type: str = 'git_clone'
    url: str = None
    to_path: str = None
    progress: Optional[str] = None
    env: Optional[dict] = None
    multi_options: Optional[list] = None
    kwargs: Optional[dict] = {}

    def execute(self):
        if not self.to_path:
            self.to_path = self.url.split('/')[-1].split('.')[0]
        if self.url:
            cloned_repo = Repo.clone_from(
                url=self.url,
                to_path=self.to_path,
                progress=self.progress,
                env=self.env,
                multi_options=self.multi_options,
                **self.kwargs,
            )
            return self.to_path
