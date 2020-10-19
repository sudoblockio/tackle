"""Context related items."""
from cookiecutter.models.mode import Mode
from cookiecutter.models.context import Context

# from cookiecutter.configs


def get_context(
    context: Context, mode: Mode,
):
    pass


# def generate_context(
#         repo_dir: str,
#         context_key,
# ):
#     template_name = os.path.basename(os.path.abspath(repo_dir))
#     if not context_key:
#         context_key = os.path.basename(context_file).split('.')[0]
#
#     if replay:
#         if isinstance(replay, bool):
#             context = load(settings.replay_dir, template_name, context_key)
#         else:
#             path, template_name = os.path.split(os.path.splitext(replay)[0])
#             context = load(path, template_name, context_key)
#
#     else:
#         context_file_path = os.path.join(repo_dir, context_file)
#         logger.debug('context_file is %s', context_file_path)
#
#         context = generate_context(
#             context_file=context_file_path,
#             default_context=settings.default_context,
#             extra_context=extra_context,
#             context_key=context_key,
#         )
#
#         # include template dir or url in the context dict
#         context[context_key]['_template'] = repo_dir
#         # include output+dir in the context dict
#         context[context_key]['_output_dir'] = os.path.abspath(output_dir)
#
#         # prompt the user to manually configure at the command line.pyth
#         # except when 'no-input' flag is set
#         context[context_key] = prompt_for_config(
#             context, context_key, existing_context, mode
#         )
#
#         dump(settings.replay_dir, template_name, context, context_key)
