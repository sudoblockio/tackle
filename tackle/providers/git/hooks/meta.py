# -*- coding: utf-8 -*-

"""Meta hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import os
import logging
import subprocess

from tackle.utils.context_manager import work_in
from tackle.models import BaseHook
from typing import Dict, List

logger = logging.getLogger(__name__)


class MetaGitHook(BaseHook):
    """
    Hook to create meta repo.

    """

    type: str = 'meta_repo'

    repos: Dict = None
    repo_tree: Dict = None

    base_dir: str = os.path.abspath(os.path.curdir)
    meta_file: str = '.meta'
    action: str = None


    def _action(self):
        if self.action:
            return

    def _git_command(self):
        p = subprocess.Popen(
            self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        output, err = p.communicate()

    def _parse_repo_tree(self):
        def flatten(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = os.path.join(parent_key, k)
                if isinstance(v, collections.MutableMapping):
                    items.extend(flatten(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)




    def execute(self):
        with work_in(self.base_dir):
            for i in self.repo_tree.keys():
                pass

        # if self.repos:
        #     if isinstance(self.repos, list):
        #         for i in self.repos:
        #             pass
