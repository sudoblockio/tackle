def key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    """

    """
    # TODO: Need to fix {{key}} keys
    value = key_to_dict_macro(context=context, key=key, value=value, arrow=arrow)
    # General
    if key == 'import':
        return import_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'return':
        return return_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'exit':
        return exit_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'raise':
        return raise_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'assert':
        return assert_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'cmd':
        return cmd_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'print':
        return print_key_macro(context=context, key=key, value=value, arrow=arrow)
    # Data manipulation
    elif key == 'merge':
        return merge_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'set':
        return set_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'update':
        return update_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'append':
        return append_key_macro(context=context, key=key, value=value, arrow=arrow)
    elif key == 'pop':
        return pop_key_macro(context=context, key=key, value=value, arrow=arrow)
    else:
        return value

    # else:
    #     return key_to_dict_macro(
    #         context=context,
    #         key=key,
    #         value=value,
    #         arrow=arrow,
    #     )
