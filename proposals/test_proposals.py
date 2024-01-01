from tackle import tackle


def test_proposal_default():
    """Default behaviour is to run update everything - GH, table, header."""
    output = tackle()

    assert output


def test_proposals_get_github_token():
    """This could fail depending on if the file / env var exists or not."""
    output = tackle('get_github_token')

    assert output


def test_proposals_github_issue_get_by_num():
    output = tackle('github_issue', 'get_by_num', 172)

    assert output['title'] == 'AST Upgrade'


def test_proposals_get_all_proposals():
    output = tackle('get_all_proposals')

    assert len(output) > 2
