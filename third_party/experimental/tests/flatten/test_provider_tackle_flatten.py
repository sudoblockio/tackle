from tackle.main import tackle


def test_provider_tackle_flatten_ls():
    output = tackle('ls.yaml', no_input=True)

    assert output['empty']['args'] == '.'
    assert output['all']['args'] == '. --all'
    assert output['almost-all']['args'] == '. --almost-all'
    assert output['arg']['args'] == '.hooks'


def test_provider_tackle_flatten_kubectl():
    output = tackle('kubectl.yaml', no_input=True)

    assert output['apply']['args']
    assert output['delete']['args']


def test_provider_tackle_flatten_method():
    output = tackle('method.yaml', no_input=True)

    assert output


def test_provider_tackle_flatten_splat():
    output = tackle('splat.yaml', no_input=True)

    assert output
