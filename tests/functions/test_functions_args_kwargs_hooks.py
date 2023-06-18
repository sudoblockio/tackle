from tackle import tackle


def test_function_supplied_kwargs_param_dict(change_curdir_fixtures):
    """
    Test that we can populate a functions fields with a `kwargs` key as a dict that is
     a dict that will update the field's values.
    """
    output = tackle('supplied-kwargs-param-dict.yaml')
    assert output['kwarg']['bar'] == 'bing'
    assert output['kwarg'] == output['call']


def test_function_supplied_kwargs_param_str(change_curdir_fixtures):
    """
    Test that we can populate a functions fields with a `kwargs` key as a str that is
     a dict that will update the field's values.
    """
    output = tackle('supplied-kwargs-param-str.yaml')
    assert output['kwarg']['bar'] == 'bing'
    assert output['kwarg'] == output['call']


def test_function_supplied_kwargs_param_str_loop(change_curdir_fixtures):
    """Check that we can use kwargs within a loop"""
    output = tackle('supplied-kwargs-param-str-loop.yaml')
    assert output['call'][0]['bar'] == 'bing'
    assert len(output['call']) == 2


def test_function_supplied_args_param_str(change_curdir_fixtures):
    """Test that we can populate a functions args with an `args` key as str."""
    output = tackle('supplied-args-param-str.yaml')
    assert output['call']['bar'] == 'bing'


def test_function_supplied_args_param_list(change_curdir_fixtures):
    """Test that we can populate a functions args with an `args` key as list."""
    output = tackle('supplied-args-param-list.yaml')
    assert output['call']['bar'] == 'bing bling'
