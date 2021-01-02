.. _calling-from-python:

Calling Cookiecutter Functions From Python
------------------------------------------

You can use Cookiecutter from Python::

    from tackle.main import tackle

    # Create project from the cookiecutter-pypackage/ template
    tackle('cookiecutter-pypackage/')

    # Create project from the cookiecutter-pypackage.git repo template
    tackle('https://github.com/audreyr/cookiecutter-pypackage.git')

This is useful if, for example, you're writing a web framework and need to
provide developers with a tool similar to `django-admin.py startproject` or
`npm init`.
