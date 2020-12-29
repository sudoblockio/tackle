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
    source = models.Source(
        template=template, password=password, checkout=checkout, directory=directory,
    )
    mode = models.Mode(no_input=no_input)
    settings = models.Settings(abbreviations=abbreviations, tackle_dir=clone_to_dir)

    return source, mode, settings
