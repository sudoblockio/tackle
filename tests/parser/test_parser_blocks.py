import pytest
import os
import yaml

from tackle import tackle

FIXTURES = [
    ('single-level.yaml', 'single-level-output.yaml'),
    ('nested-dict.yaml', 'nested-dict-output.yaml'),
    ('nested-for.yaml', 'nested-for-output.yaml'),
    ('nested-if-blocks.yaml', 'nested-for-output.yaml'),
]


@pytest.mark.parametrize("input,output", FIXTURES)
def test_parser_blocks_validate_output(chdir, input, output):
    """Test blocks."""
    chdir(os.path.join("fixtures", "blocks"))
    with open(output) as f:
        expected_output = yaml.safe_load(f)

    tackle_output = tackle(input)
    assert tackle_output == expected_output
