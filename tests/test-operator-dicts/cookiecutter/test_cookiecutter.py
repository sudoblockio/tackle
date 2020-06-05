# # -*- coding: utf-8 -*-
#
# """Tests dict input objects for `cookiecutter.prompt` module."""
#
# from cookiecutter.operators.cookiecutter import NukikataOperator
# import os
#
# context = {
#     'cookiecutter': {
#         'project_name': "Slartibartfast",
#         'details': {"type": "cookiecutter",
#                     "template": "https://github.com/insight-infrastructure/cookiecutter-terraform-terratest-aws"},
#                     "no_input": True
#     }
# }
#
#
# def test_cookiecutter():
#     """Verify simplest functionality."""
#     c = NukikataOperator(context['cookiecutter']['details'], context)
#     d = c.execute()
#     assert d.rstrip() == os.path.abspath(os.path.dirname(__file__))
