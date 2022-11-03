from ruamel.yaml import YAML

from tackle.macros import function_field_to_parseable_macro


def test_function_field_to_parseable_macro(change_curdir_fixtures, context):
    """Test that the macro is able to expand all the keys properly."""
    yaml = YAML()
    with open('func-inputs-basic.yaml') as f:
        fixture = yaml.load(f)

    output = function_field_to_parseable_macro(
        fixture['input'], context=context, func_name='f'
    )

    assert fixture['expected'] == output
