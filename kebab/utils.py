import copy
import logging

from kebab.exceptions import KebabException

_logger = logging.getLogger(__name__)


def update_recursively(value1, value2):
    """
    Update dictionary recursively.
    If they are both dicts, then take the update the keys recursively (Python extend(...) function).
    Otherwise, take the second value.

    :param str|int|float|list|dict|None value1:
    :param str|int|float|list|dict|None value2:
    :return:
    """
    if value2 is None:
        return copy.deepcopy(value1)
    elif not isinstance(value1, dict) or not isinstance(value2, dict):
        # If either d1 or d2 is not dict, then use second one.
        return copy.deepcopy(value2)
    else:
        result = copy.deepcopy(value1)
        for key in value2:
            if key in result:
                result[key] = update_recursively(result[key], value2[key])
            elif value2[key] is not None:
                result[key] = value2[key]
        return result


def fill_recursively(dictionary, key, value, delimiter='.'):
    if delimiter not in key:
        dictionary[key] = value
    else:
        next_key, remain_path = key.split(delimiter, 1)
        inner_dictionary = dictionary.setdefault(next_key, {})
        if isinstance(inner_dictionary, dict):
            try:
                fill_recursively(inner_dictionary,
                                 key=remain_path,
                                 value=value,
                                 delimiter=delimiter)
            except KebabException:
                raise KebabException(f"Unable to inflate key {key}, not a dictionary")
        else:
            raise KebabException(f"Unable to inflate key {key}, not a dictionary")


def lookup_recursively(dictionary, key, default_value=None, delimiter='.'):
    """
    If there is no delimiter, this is the last level in the path, return directly.

    If there are more delimiters, use the first part of the key to retrieve the next level of
    the dictionary and lookup recursively.

    Unless the following two situation happens:
        1. the value of current level doesn't exist
        2. the value of current level is not a dict

    :param dict dictionary:
    :param str key:
    :param Any default_value:
    :param str delimiter:
    """
    if delimiter not in key:
        # no more split, value supposed to be in this level
        return dictionary.get(key, default_value)
    else:
        next_key, remain_path = key.split(delimiter, 1)
        # the value of current level has to exist
        if next_key in dictionary:
            inner_dictionary = dictionary.get(next_key)
            # the value of current level has to be a dict
            if isinstance(inner_dictionary, dict):
                # enter next level
                return lookup_recursively(inner_dictionary,
                                          key=remain_path,
                                          default_value=default_value,
                                          delimiter=delimiter)
        return default_value


def flatten(dictionary, path=None, delimiter='_'):
    """
    Given the dictionary, flatten it to one level (separated by underscore).
    :param dict[str, any] dictionary: the dictionary to flatten
    :param list[str] path: the path to the current dictionary
    :param delimiter: the delimiter to join hierarchical keys.
    :return: flattened dictionary
    """
    path = path or []

    flattened = {}
    for child_key, child_value in dictionary.items():
        child_path = path + [child_key]
        if isinstance(child_value, dict):
            flattened.update(flatten(child_value, child_path))
        else:
            # child_value could be either a list or str, int, unicode, float, ...
            flattened[delimiter.join(child_path)] = child_value
    return flattened
