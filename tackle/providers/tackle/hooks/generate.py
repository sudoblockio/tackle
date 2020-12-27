# -*- coding: utf-8 -*-

"""Generate hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from tackle.models import BaseHook, Output, Context, Source
from tackle.generate import generate_files

logger = logging.getLogger(__name__)


# TODO: WIP - May not need but would be nice to call the generate
#  function from a hook
class GenerateHook(BaseHook):
    """
    Hook  for blocks of hooks.

    This is a special case where the hooks input variables are not rendered
    until it is later executed.

    :param items: Map of inputs
    """

    type: str = 'generate'
    project_dir: str = '.'
    output_dir: str = '.'
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True

    def execute(self):
        context = Context(
            input_dict=self.input_dict,
            output_dict=self.output_dict,
            context_key=self.context_key,
            tackle_gen='tackle',
        )

        source = Source(repo_dir=self.project_dir)

        output = Output(
            output_dir=self.output_dir,
            overwrite_if_exists=self.overwrite_if_exists,
            skip_if_file_exists=self.skip_if_file_exists,
            accept_hooks=self.accept_hooks,
        )
        generate_files(output=output, context=context, source=source)
