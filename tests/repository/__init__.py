# -*- coding: utf-8 -*-

"""Fixture to keep legacy unit tests working."""
from tackle import models


def update_source_fixtures(
    template,
    abbreviations,
    clone_to_dir,
    checkout,
    no_input,
    password=None,
    directory=None,
):
    """Mock the old cookiecutter interfece for tests."""
    context = models.Context(
        template=template,
        password=password,
        checkout=checkout,
        directory=directory,
        no_input=no_input,
        abbreviations=abbreviations,
        settings={'tackle_dir': clone_to_dir},
    )

    return context
