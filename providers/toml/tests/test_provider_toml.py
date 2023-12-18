from tackle.main import tackle


def test_provider_toml_hook_read():
    o = tackle('read.yaml', no_input=True)
    assert 'owner' in o['read'].keys()


# @pytest.fixture()
# def clean_toml():
#     """Remove outputs."""
#     yield
#     if os.path.exists('writing.toml'):
#         os.remove('writing.toml')
#
#
# def test_provider_toml_hook_write(clean_toml):
#     tackle('write.yaml', no_input=True)
#     assert os.path.exists('writing.toml')
