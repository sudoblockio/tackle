from tackle.utils.hooks import get_hook


def test_provider_arithmatic_sum(context):
    Hook = get_hook('sum')
    output = Hook(input=[1, 2, 3]).exec(context=context)

    assert output == 6


def test_provider_arithmatic_sum_attribute(context):
    Hook = get_hook('sum')
    output = Hook(
        input=[{'value': 2}, {'value': 4}, {'value': 6}],
        attribute='value',
    ).exec(context=context)

    assert output == 12
