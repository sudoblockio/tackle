"""
Utils for modifying complex dictionaries generally based on an encoded key_path which is
a list of strings for key value lookups and byte encoded integers for items in a list.
"""
from typing import TYPE_CHECKING, Any, Union

from ruyaml.comments import CommentedKeyMap

from tackle import exceptions

if TYPE_CHECKING:
    from tackle.context import Context


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
            continue
            # return '.'.join(readable_key_path)
        elif i[-2:] in ('->', '_>'):
            readable_key_path.append(i[:-2])
            continue
        if isinstance(i, bytes):
            readable_key_path.append(str(decode_list_index(i)))
        else:
            readable_key_path.append(i)
    return '.'.join(readable_key_path)


def nested_delete(element: Union[dict, list], keys: list):
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
            if isinstance(element[keys[0]], dict):
                # Case where we have an embedded
                return nested_delete(element[keys[0]], keys[1:])
            else:
                element[keys[0]] = None
                return

    if isinstance(keys[0], bytes):
        return nested_delete(element[decode_list_index(keys[0])], keys[1:])

    return nested_delete(element[keys[0]], keys[1:])


def nested_get(element: Union[dict, list], keys: list):
    """
    Getter for dictionary / list elements based on a key_path.

    :param element: A generic dictionary or list
    :param keys: A list of string and byte encoded integers.
    :return: The value from the key_path
    """
    num_elements = len(keys)

    if num_elements == 0:
        return element

    if num_elements == 1:
        if isinstance(keys[0], bytes):
            return element[decode_list_index(keys[0])]
        return element[keys[0]]

    if isinstance(keys[0], bytes):
        return nested_get(element[decode_list_index(keys[0])], keys[1:])
    return nested_get(element[keys[0]], keys[1:])


def nested_set(element: Union[dict, list], keys: list, value: Any, index: int = 0):
    """
    Set the value of an arbitrary object based on a key_path in the form of a list
     with strings for keys and byte encoded integers for indexes in a list. This
     function recurses through the element until it is at the end of the keys where it
     sets it.

    :param element: A generic dictionary or list
    :param keys: A list of string and byte encoded integers.
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
    nested_set(element=element, keys=keys, value=value, index=index + 1)


def get_target_and_key(
    context: 'Context',
    key_path: list = None,
) -> (Any, list):
    """Get the target context and key to `set_key` from."""
    is_public = True

    if key_path is None:
        key_path = context.key_path

    output_key_path = []
    for i in key_path:
        # We want the last arrow for which data namespace to write to (ie public vs private)
        if i == '_>':
            is_public = False
        elif i == '->':
            is_public = True
        else:
            output_key_path.append(i)

    if is_public:
        # We check if we are writing to a list or a dict first as dicts are default
        # but need to change the type here if we are writing to a list
        if not context.data.public:
            context.data.public = [] if isinstance(output_key_path[0], bytes) else {}
        target_context = context.data.public
    else:
        if not context.data.private:
            context.data.private = [] if isinstance(output_key_path[0], bytes) else {}
        target_context = context.data.private

    return target_context, output_key_path


def remove_arrows_from_key_path(key_path: list) -> list:
    """Remove the arrows from a key path."""
    output = []
    for i in key_path:
        if i not in ('->', '_>'):
            output.append(i)
    return output


def set_temporary_context(
    context: 'Context',
    value: Any,
    key_path: list,
) -> None:
    """
    When setting data within a block, we need to not only set the public/private data
     but also temporary data which is indexed based on the nearest keys to the block.
    """
    # Remove as many items off the key_path as we are indexed into a block
    # For instance - key_path = ['foo', 'bar'] + key_path_block = ['foo'] then
    # tmp_key_path = ['bar']
    tmp_key_path = key_path[len(context.key_path_block) :]

    if len(tmp_key_path) == 0:
        # Nothing to set in tmp context
        return

    # Check if temp data is None and create an empty dict otherwise
    if context.data.temporary is None or len(context.data.temporary) == 0:
        if isinstance(tmp_key_path[0], bytes):
            # We don't need to worry about tmp data when we are inside a list
            return
        context.data.temporary = {}
    # Clean the key path of arrows
    tmp_key_path = [i for i in tmp_key_path if i not in ('->', '_>')]

    if len(tmp_key_path) == 0:
        # Nothing to set in tmp context
        return

    nested_set(element=context.data.temporary, keys=tmp_key_path, value=value)


def get_set_temporary_context(
    context: 'Context',
) -> None:
    """
    Used in hooks with indented contexts (ie block/match), it gets the output of the
     target context (public / private) sets that value within the temporary context
     so that it can be used for rendering.
    """
    target_context, set_key_path = get_target_and_key(context, context.key_path)
    value = nested_get(element=target_context, keys=set_key_path)
    set_temporary_context(
        context=context,
        value=value,
        key_path=context.key_path,
    )


def set_key(
    context: 'Context',
    value: Any,
    key_path: list = None,
):
    """
    Wrap nested_set to set keys for both public and private hook calls.

    For public hook calls, qualifies if the hook is compact form (ie key->) or expanded
     (ie key: {->:..}) before setting the output. For private hook calls, the key and
     all parent keys without additional objects are deleted later as they might be
     used in rendering so they are added as well but their key paths are tracked for
     later deletion.
    """
    if key_path is None:
        key_path = context.key_path

    target_context, set_key_path = get_target_and_key(context, key_path=key_path)

    try:
        nested_set(target_context, set_key_path, value)
    except TypeError as e:
        raise exceptions.GeneralException(
            f"Error setting key at key=`{get_readable_key_path(set_key_path)}`\n{e}\n"
            f"target type=`{type(target_context).__name__}`.",
        )

    if len(context.key_path_block) != 0:
        # When inside a block
        if isinstance(value, (list, dict)):
            # Whenever we are writing to temporary data we want to copy that
            value = value.copy()
        # Write to temporary data
        set_temporary_context(context=context, value=value, key_path=key_path)


def _clean_item(element: Union[dict, list], item: Union[int, str], value: Any):
    if isinstance(value, dict):
        try:
            value_key = next(iter(value.keys()))
        except StopIteration:
            return
        if isinstance(value_key, CommentedKeyMap):
            new_key = next(iter(value_key.keys()))
            element[item] = "{{" + new_key + "}}"
        else:
            cleanup_unquoted_strings(value)
    elif isinstance(value, list):
        cleanup_unquoted_strings(value)


def cleanup_unquoted_strings(element: Union[dict, list]):
    """
    Cleanup a complex dict that might have unquoted templates in them which is a very
     common mistake to make when writing tackle files. Dicts could be complex with both
     lists and embedded dicts so each key needs to be visited to check. Looks for values
     like `ordereddict([('foo', None)]): None and turns them into `foo`. Input is always
     a dict.
    """
    if isinstance(element, dict):
        for k, v in element.items():
            _clean_item(element, k, v)
    elif isinstance(element, list):
        for i, v in enumerate(element):
            _clean_item(element, i, v)


def merge(a, b, path=None, update=True):
    """
    See https://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
     Merges b into a.
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx, val in enumerate(b[key]):
                    a[key][idx] = merge(
                        a[key][idx],
                        b[key][idx],
                        path + [str(key), str(idx)],
                        update=update,
                    )
            elif update:
                a[key] = b[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def _update_input_dict(input_dict: dict, update_dict: dict, arrow: str, k: str, v: Any):
    if isinstance(v, dict):
        input_dict[f"{k}{arrow}"] = update_input_dict(
            input_dict=input_dict[f"{k}{arrow}"],
            update_dict=update_dict[k],
        )
    else:
        input_dict = {
            key if key != f"{k}{arrow}" else k: value if key != f"{k}{arrow}" else v
            for key, value in input_dict.items()
        }
    return input_dict


def update_input_dict(input_dict: dict, update_dict: dict) -> dict:
    """
    Update the input dict with update_dict which in this context are treated as
     overriding the keys. Takes into account if the key is a hook and replaces that.
    """
    for k, v in update_dict.items():
        if k in input_dict:
            input_dict.update({k: v})
        # TODO: Make this dry -> split into another function
        elif f"{k}->" in input_dict:
            # If value is a dict, recurse into this dict
            input_dict = _update_input_dict(input_dict, update_dict, '->', k, v)
        elif f"{k}_>" in input_dict:
            # Same but for private hooks
            input_dict = _update_input_dict(input_dict, update_dict, '_>', k, v)
    return input_dict
