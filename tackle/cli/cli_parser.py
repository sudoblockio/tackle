"""Main `tackle` CLI."""
import collections
import json
import os
import sys
import re
import ast

import click
from rich.traceback import install

from tackle import __version__
from tackle.exceptions import (
    FailedHookException,
    InvalidModeException,
    InvalidZipRepository,
    OutputDirExistsException,
    RepositoryCloneFailed,
    RepositoryNotFound,
    UndefinedVariableInTemplate,
    UnknownExtension,
)
from tackle.utils.log import configure_logger
from tackle.main import tackle
from tackle.parser.settings import get_settings


def version_msg():
    """Return the Tackle version, location and Python powering it."""
    python_version = sys.version[:3]
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    message = 'Tackle %(version)s from {} (Python {})'
    return message.format(location, python_version)


def validate_overwrite_inputs(ctx, param, value):
    """Validate overwrite inputs."""
    for s in value.split(' '):
        if '=' not in s:
            raise click.BadParameter(
                'EXTRA_CONTEXT should contain items of the form key=value; '
                "'{}' doesn't match that form".format(value)
            )

    # Convert tuple -- e.g.: ('program_name=foobar', 'startsecs=66')
    # to dict -- e.g.: {'program_name': 'foobar', 'startsecs': '66'}
    return collections.OrderedDict(s.split('=', 1) for s in value.split(' ')) or None


def input_string_to_dict(ctx, param, value):
    """Call back to convert str to dict."""
    if value:
        if bool(re.search(r'^\{.*\}$', value)):
            # If looks like dictionary
            return ast.literal_eval(value)
        if len(value.split(' ')) == 1 and '=' not in value:
            return value
        else:
            return validate_overwrite_inputs(ctx, param, value)


def list_installed_templates(default_config, passed_config_file):
    """List installed (locally cloned) templates. Use cookiecutter --list-installed."""
    # config = get_user_config(passed_config_file, default_config)
    # cookiecutter_folder = config.get('cookiecutters_dir')
    config = get_settings()
    cookiecutter_folder = config.tackle_dir
    if not os.path.exists(cookiecutter_folder):
        click.echo(
            'Error: Cannot list installed templates. Folder does not exist: '
            '{}'.format(cookiecutter_folder)
        )
        sys.exit(-1)

    template_names = [
        folder
        for folder in os.listdir(cookiecutter_folder)
        if os.path.exists(
            os.path.join(cookiecutter_folder, folder, 'cookiecutter.json')
        )
    ]
    click.echo('{} installed templates: '.format(len(template_names)))
    for name in template_names:
        click.echo(' * {}'.format(name))


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__, '-V', '--version', message=version_msg())
@click.argument('template', required=False)
# @click.argument('extra_context', nargs=-1, callback=input_string_to_dict)
@click.option(
    u'--context-file',
    default=None,
    help=u'The input context file to parse - overrides default cookiecutter.json',
)
@click.option(
    u'--overwrite-inputs',
    callback=input_string_to_dict,
    default=None,
    help=u'Overwrite the inputs with a dictionary.',
)
@click.option(
    u'--override-inputs',
    default=None,
    help=u'Override the inputs. Anything included will not be prompted.',
)
@click.option(
    u'--existing-context',
    default=None,
    help=u'An existing context to render the input context file.',
)
@click.option(
    u'--context-key',
    default=None,
    help=u'The key to use in the output context - overrides default \'cookiecutter\'',
)
@click.option(
    u'--no-input',
    is_flag=True,
    help='Do not prompt for parameters and only use cookiecutter.json file content',
)
@click.option(
    '-c',
    '--checkout',
    help='branch, tag or commit to checkout after git clone'
)
@click.option(
    '--directory',
    help='Directory within repo that holds cookiecutter.json file '
         'for advanced repositories with multi templates in it',
)
@click.option(
    '-v', '--verbose', is_flag=True, help='Print debug information', default=False
)
@click.option(
    '--replay',
    is_flag=True,
    help='Do not prompt for parameters and only use information entered previously',
)
@click.option(
    '--replay-file',
    type=click.Path(),
    default=None,
    help='Use this file for replay instead of the default.',
)
@click.option(
    '--record',
    is_flag=True,
    help='Record the inputs to a local file "<template name>.rerun.yml".',
)
@click.option(
    '--record-file',
    type=click.Path(),
    default=None,
    help='Record the inputs to a local file "<record file>.yml".',
)
@click.option(
    '--rerun',
    is_flag=True,
    help='Reruns the inputs from a local file "<template name>.rerun.yml".',
)
@click.option(
    '--rerun-file',
    type=click.Path(),
    default=None,
    help='Reruns the inputs from a local file "<record file>.yml".',
)
@click.option(
    '-f',
    '--overwrite-if-exists',
    is_flag=True,
    help='Overwrite the contents of the output directory if it already exists',
)
@click.option(
    '-s',
    '--skip-if-file-exists',
    is_flag=True,
    help='Skip the files in the corresponding directories if they already exist',
    default=False,
)
@click.option(
    '-o',
    '--output-dir',
    default='.',
    type=click.Path(),
    help='Where to output the generated project dir into',
)
@click.option(
    '--config-file', type=click.Path(), default=None, help='User configuration file'
)
@click.option(
    '--default-config',
    is_flag=True,
    help='Do not load a config file. Use the defaults instead',
)
@click.option(
    '--debug-file',
    type=click.Path(),
    default=None,
    help='File to be used as a stream for DEBUG logging',
)
@click.option(
    '--accept-hooks',
    type=click.Choice(['yes', 'ask', 'no']),
    default='yes',
    help='Accept pre/post hooks',
)
@click.option(
    '-l', '--list-installed', is_flag=True, help='List currently installed templates.'
)
@click.option(
    '-rt', '--rich-trace', is_flag=True, help='Creates a rich traceback for debugging.'
)
def main(
        template,
        context_file,
        context_key,
        overwrite_inputs,
        override_inputs,
        existing_context,
        no_input,
        checkout,
        directory,
        verbose,
        replay,
        replay_file,
        record,
        record_file,
        rerun,
        rerun_file,
        overwrite_if_exists,
        skip_if_file_exists,
        output_dir,
        config_file,
        default_config,
        debug_file,
        accept_hooks,
        list_installed,
        rich_trace,
):
    """Create a project from a Tackle modules or Tackle templates."""
    # Set a rich traceback mode for debugging.
    if rich_trace:
        install()  # From rich

    # Commands that should work without arguments
    if list_installed:
        list_installed_templates(default_config, config_file)
        sys.exit(0)

    # Raising usage, after all commands that should work without args.
    if not template or template.lower() == 'help':
        click.echo(click.get_current_context().get_help())
        sys.exit(0)

    configure_logger(stream_level='DEBUG' if verbose else 'INFO', debug_file=debug_file)

    # If needed, prompt the user to ask whether or not they want to execute
    # the pre/post hooks.
    if accept_hooks == "ask":
        _accept_hooks = click.confirm("Do you want to execute hooks?")
    else:
        _accept_hooks = accept_hooks == "yes"

    if replay_file:
        replay = replay_file
    if record_file:
        record = record_file
    if rerun_file:
        rerun = rerun_file

    try:
        tackle(
            template,
            checkout=checkout,
            no_input=no_input,
            context_file=context_file,
            context_key=context_key,
            overwrite_inputs=overwrite_inputs,
            override_inputs=override_inputs,
            existing_context=existing_context,
            replay=replay,
            record=record,
            rerun=rerun,
            overwrite_if_exists=overwrite_if_exists,
            output_dir=output_dir,
            config_file=config_file,
            default_config=default_config,
            password=os.environ.get('COOKIECUTTER_REPO_PASSWORD'),
            directory=directory,
            skip_if_file_exists=skip_if_file_exists,
            accept_hooks=_accept_hooks,
            calling_directory=os.path.curdir,
        )
    except (
            OutputDirExistsException,
            InvalidModeException,
            FailedHookException,
            UnknownExtension,
            InvalidZipRepository,
            RepositoryNotFound,
            RepositoryCloneFailed,
    ) as e:
        click.echo(e)
        sys.exit(1)
    except UndefinedVariableInTemplate as undefined_err:
        click.echo('{}'.format(undefined_err.message))
        click.echo('Error message: {}'.format(undefined_err.error.message))

        context_str = json.dumps(undefined_err.context, indent=4, sort_keys=True)
        click.echo('Context: {}'.format(context_str))
        sys.exit(1)


if __name__ == "__main__":
    main()
