# -*- coding: utf-8 -*-

"""AWS hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from art import text2art, tprint
from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class Text2ArtHook(BaseHook):
    """Hook for `text2art`.

    Ref https://github.com/sepandhaghighi/art#1-text2art

    :param output: The message to output.
    :param font: String font name. Check `python -m art fonts` for a gallery of fonts
    :decoration: Decorations outside of the ouput.
    :return: The output
    """

    type: str = 'text2art'
    text: str = None
    font: str = 'medium'
    decoration: str = None
    chr_ignore: bool = False

    def execute(self):
        output = text2art(
            self.text,
            font=self.font,
            decoration=self.decoration,
            chr_ignore=self.chr_ignore,
        )
        print(output)
        return output


class TPrintHook(BaseHook):
    """Hook for `tprint`.

    Ref https://github.com/sepandhaghighi/art#2-tprint

    :param output: The message to output.
    :return: The output
    """

    type: str = 'tprint'
    text: str = None
    font: str = 'medium'
    decoration: str = None
    chr_ignore: bool = False

    def execute(self):
        output = tprint(
            self.text,
            font=self.font,
            decoration=self.decoration,
            chr_ignore=self.chr_ignore,
        )
        print(output)
        return output
