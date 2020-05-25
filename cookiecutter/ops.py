# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""

from cookiecutter.operators import *  # noqa
from cookiecutter.operators import BaseOperator


def run_operator(operator_dict: dict) -> list:
    """Run operator."""
    operator_output = None
    operator_list = BaseOperator.__subclasses__()
    for o in operator_list:
        if operator_dict['type'] == o.type:
            operator = o(operator_dict)
            operator_output = operator.execute()

    if not operator_output:
        print('No operator found for input %s' % operator_dict)

    return operator_output
