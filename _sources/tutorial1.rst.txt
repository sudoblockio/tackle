==========================
Getting to Know Tackle Box
==========================

.. note:: Before you begin, please install Tackle Box.
   Instructions are in :doc:`installation`.

Tackle Box is a tool for creating CLIs and generating code. To get started creating your own tackle boxes, create a new directory/repo and create a `tackle.yaml` file with a little content like so.

.. code-block:: bash

    mkdir tackle-first-try
    cd tackle-first-try

    echo '
    name: Rob # Default prompt
    greeting: "{{name}}" # Notice the rendering
    ' >> tackle.yaml

    tackle .

Here you can see the most basic functionality where each line of the file is progressively interpreted and able to use the output of the previous line as the input of the next. The second value `\{\{name\}\}` is a templating language called jinja, a powerful templating language that is used to gain access to previous entries' outputs.

Here, we only have key value pairs but to tie into other functionality offered by tackle-box, you can use hooks by declaring a special key called `type`.  There are three main prompt hooks that you should know when building tackle boxes, `input` and `select` for strings and `checkbox` for returning lists. Here is a `tackle.yaml` file showing these at work.

.. code-block:: yaml

    name:
      type: imput
      message: What is your name?





Cookiecutter is a tool for creating projects from *cookiecutters* (project
templates).

What exactly does this mean? Read on!

Case Study: cookiecutter-pypackage
-----------------------------------

*cookiecutter-pypackage* is a cookiecutter template that creates the starter
boilerplate for a Python package.

.. note:: There are several variations of it, but for this tutorial we'll use
   the original version at https://github.com/audreyr/cookiecutter-pypackage/.

Step 1: Generate a Python Package Project
------------------------------------------

Open your shell and cd into the directory where you'd like to create a starter
Python package project.

At the command line, run the cookiecutter command, passing in the link to
cookiecutter-pypackage's HTTPS clone URL like this:

.. code-block:: bash

    $ cookiecutter https://github.com/audreyr/cookiecutter-pypackage.git

Local Cloning of Project Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, cookiecutter-pypackage gets cloned to `~/.cookiecutters/` (or equivalent
on Windows). Cookiecutter does this for you, so sit back and wait.

Local Generation of Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When cloning is complete, you will be prompted to enter a bunch of values, such
as `full_name`, `email`, and `project_name`. Either enter your info, or simply
press return/enter to accept the default values.

This info will be used to fill in the blanks for your project. For example,
your name and the year will be placed into the LICENSE file.

Step 2: Explore What Got Generated
----------------------------------

In your current directory, you should see that a project got generated:

.. code-block:: bash

    $ ls
    boilerplate

Looking inside the `boilerplate/` (or directory corresponding to your `project_slug`)
directory, you should see something like this:

.. code-block:: bash

    $ ls boilerplate/
    AUTHORS.rst      MANIFEST.in      docs             tox.ini
    CONTRIBUTING.rst Makefile         requirements.txt
    HISTORY.rst      README.rst       setup.py
    LICENSE          boilerplate      tests

That's your new project!

If you open the AUTHORS.rst file, you should see something like this:

.. code-block:: rst

    =======
    Credits
    =======

    Development Lead
    ----------------

    * Audrey Roy <audreyr@gmail.com>

    Contributors
    ------------

    None yet. Why not be the first?

Notice how it was auto-populated with your (or my) name and email.

Also take note of the fact that you are looking at a ReStructuredText file.
Cookiecutter can generate a project with text files of any type.

Great, you just generated a skeleton Python package. How did that work?

Step 3: Observe How It Was Generated
------------------------------------

Let's take a look at cookiecutter-pypackage together. Open https://github.com/audreyr/cookiecutter-pypackage in a new browser window.

{{ cookiecutter.project_slug }}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find the directory called `{{ cookiecutter.project_slug }}`. Click on it. Observe
the files inside of it. You should see that this directory and its contents
corresponds to the project that you just generated.

This happens in `find.py`, where the `find_template()` method looks for the first jinja-like directory name that starts with `cookiecutter`.

AUTHORS.rst
~~~~~~~~~~~

Look at the raw version of `{{ cookiecutter.project_slug }}/AUTHORS.rst`, at
https://raw.github.com/audreyr/cookiecutter-pypackage/master/%7B%7Bcookiecutter.project_slug%7D%7D/AUTHORS.rst.

Observe how it corresponds to the `AUTHORS.rst` file that you generated.

cookiecutter.json
~~~~~~~~~~~~~~~~~

Now navigate back up to `cookiecutter-pypackage/` and look at the
`tackle.yaml` file.

You should see JSON that corresponds to the prompts and default values shown
earlier during project generation:

.. code-block:: json

	full_name: Audrey Roy Greenfeld
	email: aroy@alum.mit.edu
	github_username: audreyr
	project_name: Python Boilerplate
	project_slug: "{{ cookiecutter.project_name.lower().replace(' ', '_') }}"
	project_short_description: Python Boilerplate contains all the boilerplate you need
	  to create a Python package.
	pypi_username: "{{ cookiecutter.github_username }}"
	version: 0.1.0
	use_pytest: n
	use_pypi_deployment_with_travis: y
	create_author_file: y
	open_source_license:
	- MIT
	- BSD
	- ISCL
	- Apache Software License 2.0
	- Not open source


Questions?
----------

If anything needs better explanation, please take a moment to file an issue at https://github.com/robcxyz/tackle-box/issues with what could be improved
about this tutorial.

Summary
-------

You have learned how to use tackle box to generate your first project from a
tackle box project template.

In Tutorial 2, you'll see how to create tackle boxes of your own, from scratch.
