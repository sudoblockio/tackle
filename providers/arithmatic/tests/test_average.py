from tackle.utils.hooks import get_hook


def test_provider_arithmatic_average(context):
    Hook = get_hook('average')
    output = Hook(input=[1, 2, 3]).exec(context=context)
    assert output == 2


def test_provider_arithmatic_average_attribute(context):
    Hook = get_hook('average')
    output = Hook(
        input=[{'value': 2}, {'value': 4}, {'value': 6}],
        attribute='value',
    ).exec(context=context)

    assert output == 4.0  # Average of 2, 4, 6
