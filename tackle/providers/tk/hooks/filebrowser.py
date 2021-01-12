# -*- coding: utf-8 -*-

"""Hook plugin that inherits a base class and is made available through `type`."""
from __future__ import print_function
from __future__ import unicode_literals

import logging
from typing import Union, Set

from tackle.models import BaseHook

try:
    from tkinter import filedialog, Tk

    # from tkinter import Tk
except ImportError:
    pass

logger = logging.getLogger(__name__)


class AskOpenFilenameHook(BaseHook):
    """
    Hook for tk's askopenfilename popup.

    :param initial_dir:
    :param filetypes:
    :param title:

    :return file location
    """

    type: str = "askopenfilename"
    initial_dir: str = "/"
    filetypes: Union[dict, Set[tuple]] = None
    title: str = "Select file"

    def execute(self):
        # Convert from dict to set of tuples
        if self.filetypes:
            self.filetypes = set(self.filetypes.items())
        else:
            self.filetypes = {("all files", "*.*")}

        root = Tk()
        root.mainloop()
        root.filename = filedialog.askopenfilename(
            initialdir=self.initial_dir, title=self.title, filetypes=self.filetypes
        )
        root.destroy()
        print(root.filename)
        return root.filename
