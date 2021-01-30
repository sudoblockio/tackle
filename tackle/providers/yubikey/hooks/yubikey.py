# # -*- coding: utf-8 -*-
#
# """Hook plugin that inherits a base class and is made available through `type`."""
# from __future__ import print_function
# from __future__ import unicode_literals
#
# import logging
# import re
# import toml
# from typing import Union, Dict, List, Any
# import sys
# import yubico
#
# from tackle.models import BaseHook
# from tackle.utils import merge_configs
#
# logger = logging.getLogger(__name__)
#
#
# class YubikeyHook(BaseHook):
#     """
#     Hook for toml.
#
#     """
#
#     type: str = 'toml'
#
#     def execute(self):
#
#         try:
#             yubikey = yubico.find_yubikey(debug=False)
#             print("Version: {}".format(yubikey.version()))
#         except yubico.yubico_exception.YubicoError as e:
#             print("ERROR: {}".format(e.reason))
#             sys.exit(1)
