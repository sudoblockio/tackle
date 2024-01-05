import pytest

from tackle.main import tackle


@pytest.mark.slow
def test_provider_requests_get():
    output = tackle('get.yaml', hooks_dir="../hooks")

    assert 'args' in output['compact']


@pytest.mark.slow
def test_provider_requests_post():
    output = tackle('post.yaml')

    assert output['expanded']['json']['stuff'] == "things"
    assert output['expanded']['json'] == output['compact']['json']


@pytest.mark.slow
def test_provider_requests_put():
    output = tackle('put.yaml')
    assert output['expanded']['json']['stuff'] == "things"


@pytest.mark.slow
def test_provider_requests_patch():
    output = tackle('patch.yaml')

    assert output['expanded']['json']['stuff'] == "things"


@pytest.mark.slow
def test_provider_requests_delete():
    output = tackle('delete.yaml')
    assert output['expanded'] == 200
