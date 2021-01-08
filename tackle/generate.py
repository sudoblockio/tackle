"""Functions for generating a project from a project template."""
import fnmatch
import logging
import os
import shutil

from binaryornot.check import is_binary
from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError, UndefinedError

from tackle.render.environment import StrictEnvironment
from tackle.exceptions import (
    FailedHookException,
    NonTemplatedInputDirException,
    OutputDirExistsException,
    UndefinedVariableInTemplate,
)
from tackle.hooks import run_hook
from tackle.utils.paths import rmtree, make_sure_path_exists
from tackle.utils.context_manager import work_in

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context, Source, Output


logger = logging.getLogger(__name__)


def is_copy_only_path(path, context, context_key='cookiecutter'):
    """Check whether the given `path` should only be copied and not rendered.

    Returns True if `path` matches a pattern in the given `context` dict,
    otherwise False.

    :param path: A file-system path referring to a file or dir that
        should be rendered or just copied.
    :param context: cookiecutter context.
    """
    try:
        for dont_render in context[context_key]['_copy_without_render']:
            if fnmatch.fnmatch(path, dont_render):
                return True
    except KeyError:
        return False

    return False


def generate_file(project_dir, context: 'Context', output: 'Output'):
    """Render filename of infile as name of outfile, handle infile correctly.

    Dealing with infile appropriately:

        a. If infile is a binary file, copy it over without rendering.
        b. If infile is a text file, render its contents and write the
           rendered infile to outfile.

    Precondition:

        When calling `generate_file()`, the root template dir must be the
        current working directory. Using `utils.work_in()` is the recommended
        way to perform this directory change.

    :param project_dir: Absolute path to the resulting generated project.
    :param infile: Input file to generate the file from. Relative to the root
        template dir.
    :param context: Dict for populating the cookiecutter's variables.
    :param env: Jinja2 template execution environment.
    """
    logger.debug('Processing file %s', output.infile)

    # Render the path to the output file (not including the root project dir)
    outfile_tmpl = output.env.from_string(output.infile)

    from tackle.render import build_render_context

    render_context = build_render_context(context)

    outfile = os.path.join(project_dir, outfile_tmpl.render(**render_context))
    file_name_is_empty = os.path.isdir(outfile)
    if file_name_is_empty:
        logger.debug('The resulting file name is empty: %s', outfile)
        return

    if output.skip_if_file_exists and os.path.exists(outfile):
        logger.debug('The resulting file already exists: %s', outfile)
        return

    logger.debug('Created file at %s', outfile)

    # Just copy over binary files. Don't render.
    logger.debug("Check %s to see if it's a binary", output.infile)
    if is_binary(output.infile):
        logger.debug(
            'Copying binary %s to %s without rendering', output.infile, outfile
        )
        shutil.copyfile(output.infile, outfile)
    else:
        # Force fwd slashes on Windows for get_template
        # This is a by-design Jinja issue
        infile_fwd_slashes = output.infile.replace(os.path.sep, '/')

        # Render the file
        try:
            tmpl = output.env.get_template(infile_fwd_slashes)
        except TemplateSyntaxError as exception:
            # Disable translated so that printed exception contains verbose
            # information about syntax error location
            exception.translated = False
            raise
        rendered_file = tmpl.render(**render_context)

        # Detect original file newline to output the rendered file
        # note: newline='' ensures newlines are not converted
        with open(output.infile, 'r', encoding='utf-8', newline='') as rd:
            rd.readline()  # Read the first line to load 'newlines' value

            # Use `_new_lines` overwrite from context, if configured.
            newline = rd.newlines
            if context.input_dict[context.context_key].get('_new_lines', False):
                newline = context.input_dict[context.context_key]['_new_lines']
                logger.debug('Overwriting end line character with %s', newline)

        logger.debug('Writing contents to file %s', outfile)

        with open(outfile, 'w', encoding='utf-8', newline=newline) as fh:
            fh.write(rendered_file)

    # Apply file permissions to output file
    shutil.copymode(output.infile, outfile)


def render_and_create_dir(dirname, context: 'Context', output: 'Output'):
    """Render name of a directory, create the directory, return its path."""
    name_tmpl = output.env.from_string(dirname)

    from tackle.render import build_render_context

    render_context = build_render_context(context)
    rendered_dirname = name_tmpl.render(render_context)
    # rendered_dirname = name_tmpl.render(**context.input_dict)

    dir_to_create = os.path.normpath(os.path.join(output.output_dir, rendered_dirname))

    logger.debug(
        'Rendered dir %s must exist in output_dir %s', dir_to_create, output.output_dir
    )

    output_dir_exists = os.path.exists(dir_to_create)

    if output_dir_exists:
        if output.overwrite_if_exists:
            logger.debug(
                'Output directory %s already exists, overwriting it', dir_to_create
            )
        else:
            msg = 'Error: "{}" directory already exists'.format(dir_to_create)
            raise OutputDirExistsException(msg)
    else:
        make_sure_path_exists(dir_to_create)

    return dir_to_create, not output_dir_exists


def ensure_dir_is_templated(dirname):
    """Ensure that dirname is a templated directory name."""
    if '{{' in dirname and '}}' in dirname:
        return True
    else:
        raise NonTemplatedInputDirException


def _run_hook_from_repo_dir(
    repo_dir, hook_name, project_dir, delete_project_on_failure, context: 'Context'
):
    """Run hook from repo directory, clean project directory if hook fails.

    :param repo_dir: Project template input directory.
    :param hook_name: The hook to execute.
    :param project_dir: The directory to execute the script from.
    :param context: Tackle project context.
    :param delete_project_on_failure: Delete the project directory on hook
        failure?
    """
    with work_in(repo_dir):
        # run_hook(hook_name, project_dir, context)
        try:
            run_hook(hook_name, project_dir, context)
        except FailedHookException:
            if delete_project_on_failure:
                rmtree(project_dir)
            logger.error(
                "Stopping generation because %s hook "
                "script didn't exit successfully",
                hook_name,
            )
            raise


def find_template(repo_dir, context: 'Context'):
    """Determine which child directory of `repo_dir` is the project template.

    :param input_dict: The input dict to search for keys to match for renderable dirs.
    :param repo_dir: Local directory of newly cloned repo.
    :returns project_template: Relative path to project template.
    """
    logger.debug('Searching %s for the project template.', repo_dir)
    repo_dir_contents = os.listdir(repo_dir)

    project_template = None
    for item in repo_dir_contents:
        if context.tackle_gen == 'cookiecutter':
            if context.context_key in item and '{{' in item and '}}' in item:
                project_template = item
                break
        else:
            if (
                item.strip('{{').strip('}}') in context.output_dict.keys()
                and '{{' in item  # noqa
                and '}}' in item  # noqa
            ):
                project_template = item
                break

    if project_template:
        project_template = os.path.join(repo_dir, project_template)
        logger.debug('The project template appears to be %s', project_template)
        return project_template
    else:
        return None


def generate_files(output: 'Output', context: 'Context', source: 'Source'):
    """Render the templates and saves them to files.

    :param repo_dir: Project template input directory.
    :param context: Dict for populating the template's variables.
    :param output_dir: Where to output the generated project dir into.
    :param overwrite_if_exists: Overwrite the contents of the output directory
        if it exists.
    :param accept_hooks: Accept pre and post hooks if set to `True`.
    """
    template_dir = find_template(source.repo_dir, context)
    if template_dir:
        envvars = context.input_dict.get(context.context_key, {}).get(
            '_jinja2_env_vars', {}
        )

        unrendered_dir = os.path.split(template_dir)[1]
        ensure_dir_is_templated(unrendered_dir)
        output.env = StrictEnvironment(
            context=context.input_dict, keep_trailing_newline=True, **envvars
        )
        try:
            project_dir, output_directory_created = render_and_create_dir(
                unrendered_dir, context, output
            )
        except UndefinedError as err:
            msg = "Unable to create project directory '{}'".format(unrendered_dir)
            raise UndefinedVariableInTemplate(msg, err, context.input_dict)

        # We want the Jinja path and the OS paths to match. Consequently, we'll:
        #   + CD to the template folder
        #   + Set Jinja's path to '.'
        #
        #  In order to build our files to the correct folder(s), we'll use an
        # absolute path for the target folder (project_dir)
        project_dir = os.path.abspath(project_dir)
        logger.debug('Project directory is %s', project_dir)

        # if we created the output directory, then it's ok to remove it
        # if rendering fails
        delete_project_on_failure = output_directory_created

        if output.accept_hooks:
            _run_hook_from_repo_dir(
                source.repo_dir,
                'pre_gen_project',
                project_dir,
                delete_project_on_failure,
                context,
            )

        with work_in(template_dir):
            output.env.loader = FileSystemLoader('.')

            for root, dirs, files in os.walk('.'):
                # We must separate the two types of dirs into different lists.
                # The reason is that we don't want ``os.walk`` to go through the
                # unrendered directories, since they will just be copied.
                copy_dirs = []
                render_dirs = []

                for d in dirs:
                    d_ = os.path.normpath(os.path.join(root, d))
                    # We check the full path, because that's how it can be
                    # specified in the ``_copy_without_render`` setting, but
                    # we store just the dir name
                    if is_copy_only_path(d_, context.input_dict):
                        copy_dirs.append(d)
                    else:
                        render_dirs.append(d)

                for copy_dir in copy_dirs:
                    indir = os.path.normpath(os.path.join(root, copy_dir))
                    outdir = os.path.normpath(os.path.join(project_dir, indir))
                    outdir = output.env.from_string(outdir).render(**context.input_dict)
                    logger.debug(
                        'Copying dir %s to %s without rendering', indir, outdir
                    )
                    shutil.copytree(indir, outdir)

                # We mutate ``dirs``, because we only want to go through these dirs
                # recursively
                dirs[:] = render_dirs
                for d in dirs:
                    unrendered_dir = os.path.join(project_dir, root, d)
                    try:
                        render_and_create_dir(unrendered_dir, context, output)
                    except UndefinedError as err:
                        if delete_project_on_failure:
                            rmtree(project_dir)
                        _dir = os.path.relpath(unrendered_dir, output.output_dir)
                        msg = "Unable to create directory '{}'".format(_dir)
                        raise UndefinedVariableInTemplate(msg, err, context.input_dict)

                for f in files:
                    output.infile = os.path.normpath(os.path.join(root, f))
                    if is_copy_only_path(output.infile, context.input_dict):
                        outfile_tmpl = output.env.from_string(output.infile)
                        outfile_rendered = outfile_tmpl.render(**context.input_dict)
                        outfile = os.path.join(project_dir, outfile_rendered)
                        logger.debug(
                            'Copying file %s to %s without rendering',
                            output.infile,
                            outfile,
                        )
                        shutil.copyfile(output.infile, outfile)
                        shutil.copymode(output.infile, outfile)
                        continue
                    try:
                        generate_file(project_dir, context, output)

                    except UndefinedError as err:
                        if delete_project_on_failure:
                            rmtree(project_dir)
                        msg = "Unable to create file '{}'".format(output.infile)
                        raise UndefinedVariableInTemplate(msg, err, context.input_dict)

        if output.accept_hooks:
            _run_hook_from_repo_dir(
                source.repo_dir,
                'post_gen_project',
                project_dir,
                delete_project_on_failure,
                context,
            )

            for hook in context.post_gen_hooks:
                hook.execute()

            logger.debug('Resulting project directory created at %s', project_dir)
            return project_dir
    else:
        if output.accept_hooks:
            _run_hook_from_repo_dir(
                source.repo_dir,
                'post_gen_project',
                '.',  # TODO: This needs context switching
                False,
                context,
            )

        for hook in context.post_gen_hooks:
            hook.execute()

        logger.debug('No project directory was created')
        return None
