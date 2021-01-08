"""Collection of tests around cookiecutter's replay feature."""

import os
from tackle.main import tackle


# TODO: Fix with replay
# def test_replay_dump_template_name(
#     monkeypatch, mocker, user_config_data, user_config_file
# ):
#     """Check that replay_dump is called with a valid template_name.
#
#     Template name must not be a relative path.
#
#     Otherwise files such as ``..json`` are created, which are not just cryptic
#     but also later mistaken for replay files of other templates if invoked with
#     '.' and '--replay'.
#
#     Change the current working directory temporarily to 'tests/legacy/fixtures/fake-repo-tmpl'
#     for this test and call cookiecutter with '.' for the target template.
#     """
#     monkeypatch.chdir(
#         os.path.join(
#             os.path.abspath(os.path.dirname(__file__)),
#             '..',
#             'legacy',
#             'fixtures',
#             'fake-repo-tmpl',
#         )
#     )
#
#     mock_replay_dump = mocker.patch('cookiecutter.main.dump')
#     mocker.patch('cookiecutter.main.generate_files')
#
#     tackle(
#         '.', no_input=True, replay=False, config_file=user_config_file,
#     )
#
#     mock_replay_dump.assert_called_once_with(
#         user_config_data['replay_dir'], 'fake-repo-tmpl', mocker.ANY, 'cookiecutter',
#     )


# def test_replay_load_template_name(
#     monkeypatch, mocker, user_config_data, user_config_file
# ):
#     """Check that replay_load is called correctly.
#
#     Calls require valid template_name that is not a relative path.
#
#     Change the current working directory temporarily to 'tests/legacy/fixtures/fake-repo-tmpl'
#     for this test and call cookiecutter with '.' for the target template.
#     """
#     monkeypatch.chdir(
#         os.path.join(
#             os.path.abspath(os.path.dirname(__file__)),
#             '..',
#             'fixtures',
#             'fake-repo-tmpl',
#         )
#     )
#
#     mock_replay_load = mocker.patch('cookiecutter.main.load')
#     mocker.patch('cookiecutter.main.generate_files')
#
#     cookiecutter(
#         '.', replay=True, config_file=user_config_file,
#     )
#
#     mock_replay_load.assert_called_once_with(
#         user_config_data['replay_dir'], 'fake-repo-tmpl', 'cookiecutter'
#     )


# TODO: Fix with replay
# def test_custom_replay_file(change_dir_main_fixtures, monkeypatch, mocker, user_config_file):
#     """Check that reply.load is called with the custom replay_file."""
#     monkeypatch.chdir('fake-repo-tmpl')
#
#     mock_replay_load = mocker.patch('cookiecutter.main.load')
#     mocker.patch('cookiecutter.generate.generate_files')
#
#     tackle(
#         '.', replay='./custom-replay-file', config_file=user_config_file,
#     )
#
#     mock_replay_load.assert_called_once_with('.', 'custom-replay-file', 'cookiecutter')


def test__embed(change_dir_main_fixtures, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    context = tackle(
        'fake-repo-tmpl-tackle-embed', no_input=True, output_dir=str(tmpdir)
    )

    assert 'sterf' in list(context['stuff'].keys())
