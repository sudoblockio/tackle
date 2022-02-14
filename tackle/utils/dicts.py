"""
Utils for modifying complex dictionaries generally based on an encoded key_path which is
a list of strings for key value lookups and byte encoded integers for items in a list.
"""
from typing import Union


def encode_list_index(list_index: int) -> bytes:
    """Encode an index for lists in a key path to bytes."""
    return list_index.to_bytes(2, byteorder='big')


def decode_list_index(list_index: bytes) -> int:
    """Decode an index for lists in a key path from bytes."""
    return int.from_bytes(list_index, byteorder='big')


def encode_key_path(path: Union[list, str], sep: str = "/") -> list:
    """
    Take a list or string key_path and encode it with bytes for items in a list. Strings
    are split up based on a separator, ie path/to/key.
    """
    if isinstance(path, str):
        path = path.split(sep)
        for i, v in enumerate(path):
            try:
                # Try to convert strings to ints
                path[i] = int(v)
            except ValueError:
                pass
        path = [i if not isinstance(i, int) else encode_list_index(i) for i in path]

    # Need to encode keys into bytes as that is how internally the parser works so
    # it doesn't jam up on any integer key. This hook will fail if the key is an
    # int.
    path = [i if not isinstance(i, int) else encode_list_index(i) for i in path]
    if isinstance(path, dict):
        # Could have key path expressed as dict?
        raise NotImplementedError

    return path


def get_key_from_key_path(key_path: list) -> str:
    """Take key_path and return the nearest key from end removing arrows."""
    if key_path[-1] in ('->', '_>'):
        # Expanded key
        return key_path[-2]
    elif key_path[-1].endswith('->', '_>'):
        # Compact key
        return key_path[-1][:-2]


def get_readable_key_path(key_path: list) -> str:
    """Take key_path and return the nearest key from end removing arrows."""
    readable_key_path = []
    for i in key_path:
        if i in ('->', '_>'):
            return '.'.join(readable_key_path)
        elif i[-2:] in ('->', '_>'):
            readable_key_path.append(i[:-2])
            return '.'.join(readable_key_path)
        if isinstance(i, bytes):
            readable_key_path.append(decode_list_index(i))
        else:
            readable_key_path.append(i)


def nested_delete(element, keys):
    """
    Delete items in a generic element (list / dict) based on a key path in the form of
    a list with strings for keys and byte encoded integers for indexes in a list.
    """
    num_elements = len(keys)

    if num_elements == 1:
        if isinstance(keys[0], bytes):
            element.pop(decode_list_index(keys[0]))
            return element

        elif isinstance(element, dict):
            element.pop(keys[0])
            return

    elif num_elements == 2:
        if isinstance(keys[0], bytes) and isinstance(keys[1], str):
            # Case for when we have an embedded item in a list but don't know if it is
            # a map with multiple keys that needs to have a single key removed or the
            # whole item itself
            # TODO
            if isinstance(element[decode_list_index(keys[0])], dict):
                # Further inspection to see if there are any other keys in the dict.
                # If not, then remove the whole item otherwise recurse
                if len(element[decode_list_index(keys[0])].keys()) == 1:
                    element.pop(decode_list_index(keys[0]))
                    return

                return nested_delete(element[decode_list_index(keys[0])], keys[1:])
        elif isinstance(keys[0], str) and isinstance(keys[1], bytes):
            return nested_delete(element[keys[0]], keys[1:])

        elif isinstance(keys[0], str) and isinstance(keys[1], str):
            #
            if isinstance(element[keys[0]], dict):
                # Case where we have an embedded
                return nested_delete(element[keys[0]], keys[1:])
            else:
                # element.pop(keys[0])
                element[keys[0]] = None
                return

    if isinstance(keys[0], bytes):
        return nested_delete(element[decode_list_index(keys[0])], keys[1:])

    return nested_delete(element[keys[0]], keys[1:])


def nested_get(element, keys):
    """
    Getter for dictionary / list elements based on a key_path.

    :param element: A generic dictionary or list
    :param keys: List of string and byte encoded integers.
    :return: The value from the key_path
    """
    num_elements = len(keys)

    if num_elements == 1:
        if isinstance(keys[0], bytes):
            return element[decode_list_index(keys[0])]
        return element[keys[0]]

    if isinstance(keys[0], bytes):
        return nested_get(element[decode_list_index(keys[0])], keys[1:])
    return nested_get(element[keys[0]], keys[1:])


def nested_set(element, keys, value, index: int = 0):
    """
    Set the value of an arbitrary object based on a key_path in the form of a list
    with strings for keys and byte encoded integers for indexes in a list. This function
    recurses through the element until it is at the end of the keys where it sets it.

    :param element: A generic dictionary or list
    :param keys: List of string and byte encoded integers.
    :param value: The value to set
    :param index: Index is only used when called recursively, not initially
    """
    num_elements = len(keys)
    # Check if we are at the last element of the list to insert the value
    if index == num_elements - 1:
        if isinstance(keys[-1], bytes):
            element.insert(decode_list_index(keys[-1]), value)
        else:
            element[keys[-1]] = value
        return

    if isinstance(element, dict):
        # Look ahead if the next item is a list
        if isinstance(keys[index + 1], bytes):
            element = element.setdefault(keys[index], [])
        else:
            element = element.setdefault(keys[index], {})

    # element must be list
    # Check if we are updating an existing element
    elif len(element) > decode_list_index(keys[index]):
        element = element[decode_list_index(keys[index])]
    else:
        if isinstance(keys[index + 1], bytes):
            element.insert(decode_list_index(keys[index]), [])
        else:
            element.insert(decode_list_index(keys[index]), {})
        element = element[decode_list_index(keys[index])]
    nested_set(element, keys, value, index + 1)


def set_key(element, keys: list, value, append_hook_value: bool = False):
    """
    Wrap nested_set to set keys for both public and private hook calls.

    For public hook calls, qualifies if the hook is compact form (ie key->) or expanded
    (ie key: {->:..}) before setting the output. For private hook calls, the key and
    all parent keys without additional objects are deleted later as they might be
    used in rendering so they are added as well but their key paths are tracked for
    later deletion.
    """
    # TODO: Implement removal of parent keys without values
    if isinstance(keys[-1], bytes):
        if append_hook_value:
            # Condition when we are appending values from a hook for loop where we need
            # take off the prior keys hook arrows
            parent_key_value = keys[-2]
            if parent_key_value in ('->', '_>'):
                # We never append with the hook arrow so temporarily remove it so we can
                # still keep the path to the key
                keys.pop(-2)
                nested_set(element, keys, value)
                keys.insert(-1, parent_key_value)
            else:
                # Same as above but here we are in a compact expression and want to
                # temporarily replace the trailing hook arrow
                keys[-2] = parent_key_value.replace('->', '').replace('_>', '')
                nested_set(element, keys, value)
                keys[-2] = parent_key_value
        else:
            # Condition when we are appending values from a list
            nested_set(element, keys, value)

    elif keys[-1] == '->':  # Expanded public hook call
        nested_set(element, keys[:-1], value)
    elif keys[-1].endswith('->'):  # Compact public hook call
        nested_set(element, keys[:-1] + [keys[-1][:-2]], value)
    elif keys[-1] == '_>':  # Expanded private hook call
        nested_set(element, keys[:-1], value)
    elif keys[-1].endswith('_>'):  # Compact private hook call
        key_path = keys[:-1] + [keys[-1][:-2]]
        nested_set(element, key_path, value)
