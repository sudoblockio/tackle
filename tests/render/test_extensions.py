from tackle import tackle


def test_render_extensions_(change_curdir_fixtures):
    output = tackle('extensions.yaml')
    assert output['jsonify'].startswith('json\n"{')
