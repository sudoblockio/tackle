# -*- coding: utf-8 -*-

"""Block hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from _collections import OrderedDict
from typing import Dict

from tackle.models import BaseHook, Context, Mode, Source
import tackle as tkl


logger = logging.getLogger(__name__)


class BlockHook(BaseHook):
    """
    Hook  for blocks of hooks.

    This is a special case where the hooks input variables are not rendered
    until it is later executed.

    :param items: Map of inputs
    """

    type: str = 'block'
    items: Dict

    def execute(self):
        context = Context(
            input_dict=OrderedDict({self.context_key: self.items}),
            output_dict=OrderedDict(self.output_dict),
            overwrite_inputs=self.overwrite_inputs,
            override_inputs=self.override_inputs,
            context_key=self.context_key,
        )
        mode = Mode(no_input=self.no_input)
        source = Source()

        output = tkl.parser.context.parse_context(
            context=context, mode=mode, source=source,
        )

        return dict(output.output_dict)
