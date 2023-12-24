from tackle.utils.hooks import get_hook


def test_provider_arithmatic_modulo():
    Hook = get_hook('modulo')

    # Test without the 'equal_to' field
    output = Hook(input=10, divisor=3).exec()
    assert output == 10 % 3  # Expected modulo result

    # Test with the 'equal_to' field where the condition is met
    output = Hook(input=10, divisor=3, equal_to=1).exec()
    assert output is True  # 10 % 3 == 1

    # Test with the 'equal_to' field where the condition is not met
    output = Hook(input=10, divisor=3, equal_to=2).exec()
    assert output is False  # 10 % 3 != 2
