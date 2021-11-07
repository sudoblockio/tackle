from typing import Any, Union


def remove_tackle_hook_key(key: str) -> str:
    """Remove the ending hook key."""
    # if key.startswith('<'):
    if key.endswith('<'):
        return key[1:]
    else:
        return key


def nested_get(element, keys):
    num_elements = len(keys)

    if num_elements == 1:
        if isinstance(keys[0], list):
            return element[keys[0][0]]

        try:
            x = element[keys[0]]
        except Exception:
            print()
        return element[keys[0]]

    if isinstance(keys[0], list):
        return nested_get(element[keys[0][0]], keys[1:])
    y = keys[1:]
    z = element[keys[0]]
    x = nested_get(element[keys[0]], keys[1:])
    return nested_get(element[keys[0]], keys[1:])


def nested_set(
    element,
    keys,
    value,
    index: int = 0,  # Index is only used when called recursively, not initially
):
    # TODO: Bring in the context and use for the - ?
    num_elements = len(keys)
    i = 0

    if isinstance(element, dict):
        # Drilling down into nested element
        for i, key in enumerate(keys[index:-1]):
            i += index
            if isinstance(keys[i + 1], list):
                # Means we are in a list so we must first check if it is empty
                if keys[i + 1] == [0]:
                    # If the list is empty, make it a list
                    element = element.setdefault(key, [])
                else:
                    # Otherwise drill down into a key
                    element = element.setdefault(key, element[key])

                # Check if we are able to access forward elements for list parsing recursion
                if num_elements > i + 2:
                    # Means we have an embedded dict within the list
                    # Check that there is not an element in the list yet to update.
                    if len(element) <= keys[i + 1][0]:
                        # We don't have an element so we need to add one

                        # Check if we are at the last element of the list
                        if i + 2 == num_elements - 1:
                            # Special case that we know we are at the end of a list of
                            # keys and we
                            element.append({keys[i + 2]: value})
                            return

                        if isinstance(keys[i + 3], list):
                            # Here we are at a case where we have a key path with a
                            # list index key with only one key so we must append a
                            # list instead of a dict
                            element.append({keys[i + 2]: []})
                            element = element[keys[i + 1][0]][keys[i + 2]]

                            # Recursion
                            nested_set(element, keys, value, index=i + 1)
                            return
                        else:
                            # Here we have an embeded dict within the list
                            element.append({keys[i + 2]: {}})

                    # Update to the index in the list based on the list index key
                    element = element[keys[i + 1][0]]

                    # Recursion
                    nested_set(element, keys, value, index=i + 2)
                    return
            else:
                # Traverse down the dict
                element = element.setdefault(keys[i], {})

    if isinstance(element, dict):
        # Update for k/v pairs
        # If it is dict update the indexed value
        element[keys[-1]] = value
    else:
        # Append for lists
        element.append(value)


def remove_private_vars(output_dict):
    output_dict
    pass


# https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries/25270947#25270947

#
# def nested_set(
#         element: Union[dict, list],
#         keys: list,
#         value: Any,
#         index: int = 0  # Index is only used when called recursively, not initially
# ):
#     # TODO: Bring in the context and use for the
#     num_elements = len(keys)
#     i = 0
#
#     if isinstance(element, dict):
#         # Drilling down into nested element
#         for i, key in enumerate(keys[index:-1]):
#             i += index
#             if isinstance(keys[i + 1], list):
#                 # Means we are in a list so we must first check if it is empty
#                 if keys[i + 1] == [0]:
#                     # If the list is empty, make it a list
#                     element = element.setdefault(key, [])
#                 else:
#                     # Otherwise drill down into a key
#                     element = element.setdefault(key, element[key])
#
#                 # Check if we are able to access forward elements for list parsing recursion
#                 if num_elements > i + 2:
#                     # Means we have an embedded dict within the list
#                     # Check that there is not an element in the list yet to update.
#                     if len(element) <= keys[i + 1][0]:
#                         # We don't have an element so we need to add one
#
#                         # Check if we are at the last element of the list
#                         if i + 2 == num_elements - 1:
#                             # Special case that we know we are at the end of a list of
#                             # keys
#                             element.append({keys[i + 2]: value})
#                             return
#
#                         if isinstance(keys[i+3], list):
#                             # Here we are at a case where we have a key path with a
#                             # list index key with only one key so we must append a
#                             # list instead of a dict
#                             element.append({keys[i + 2]: []})
#                             element = element[keys[i + 1][0]][keys[i + 2]]
#
#                             # Recursion
#                             nested_set(element, keys, value, index=i + 1)
#                             return
#                         else:
#                             # Here we have an embeded dict within the list
#                             element.append({keys[i + 2]: {}})
#
#                     # Update to the index in the list based on the list index key
#                     element = element[keys[i + 1][0]]
#
#                     # Recursion
#                     nested_set(element, keys, value, index=i + 2)
#                     return
#             else:
#                 # Traverse down the dict
#                 element = element.setdefault(keys[i], {})
#
#     if isinstance(element, dict):
#         # Update for k/v pairs
#         # If it is dict update the indexed value
#         element[keys[-1]] = value
#     else:
#         # Append for lists
#         element.append(value)
#
#
# def nested_get(
#         context: 'Context',
#         key,
#         value,
# ):
#     for key in context.key_path:
#         if isinstance(key, str):
#             pass
#     return context.output_dict
