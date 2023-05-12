import os
import pytest
import json
from ruamel.yaml import YAML

from tackle.cli import main

FIXTURES = [
    ('cli-call-func.yaml', 'cli-call-func-output.yaml', 'func_a'),
]


@pytest.mark.parametrize("fixture,expected_output,argument", FIXTURES)
def test_function_model_extraction(chdir, fixture, expected_output, argument, capsys):
    chdir('cli-fixtures')
    main([fixture, argument, "-p"])
    output = capsys.readouterr().out

    yaml = YAML()
    with open(expected_output) as f:
        expected_output = yaml.load(f)

    assert json.loads(output) == expected_output


@pytest.mark.parametrize("fixture,expected_output,argument", FIXTURES)
def test_function_model_extraction_in_directory(
    chdir, fixture, expected_output, argument, capsys
):
    chdir('cli-fixtures')
    yaml = YAML()
    with open(expected_output) as f:
        expected_output = yaml.load(f)

    os.chdir("a-dir")
    main([fixture, argument, "-p", "--find-in-parent"])
    output = capsys.readouterr().out

    assert json.loads(output) == expected_output


def test_function_cli_multiple_args(change_curdir_fixtures, capsys):
    main(['supplied-args-param-str.yaml', 'foo', 'bing', 'bang', '-pf', 'yaml'])
    output = capsys.readouterr().out

    assert 'bar: bing bang' in output