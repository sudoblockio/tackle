from tackle.main import tackle


def test_provider_tackle_flatten_ls(change_dir):
    output = tackle('ls.yaml', no_input=True)

    assert output['empty']['args'] == '.'
    assert output['all']['args'] == '. --all'
    assert output['almost-all']['args'] == '. --almost-all'
    assert output['arg']['args'] == '.hooks'


def test_provider_tackle_flatten_kubectl(change_dir):
    output = tackle('kubectl.yaml', no_input=True)

    assert output['apply']['args']
    assert output['delete']['args']
