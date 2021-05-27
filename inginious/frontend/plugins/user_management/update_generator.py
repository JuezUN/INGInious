from collections import OrderedDict
from inginious.frontend.plugins.user_management.utils import get_collection_document
import re


def change_name(username, param, collections_manager):
    user_filter = {
        "username": username
    }
    new_name = {
        "$set": {"realname": param}
    }
    settings = {
        "upsert": False,
    }
    collections_manager.make_update("users", user_filter, new_name, settings)


def change_email(username, param, collections_manager):
    user_filter_users = {
        "username": username
    }
    new_email_users = {
        "$set": {"email": param}
    }
    settings = {
        "upsert": False,
    }
    collections_manager.make_update("users", user_filter_users, new_email_users, settings)


def change_username(username, new_username, collection_manager, collection_name_list):
    collection_information_list = get_collection_document()
    default_collection_information = [{"path": "username", "index_array": []}]
    count = 0
    for collection_name in collection_name_list:
        if collection_name in collection_information_list:
            information = collection_information_list[collection_name]
        else:
            information = default_collection_information
        count += _crete_update_to_change_username_collection(username, new_username, collection_name, information,
                                                             collection_manager)
    return count


def _crete_update_to_change_username_collection(username, new_username, coll_name, collection_info, collection_manager):
    count = 0
    for info in collection_info:
        ans = _create_update_to_change_username(username, new_username, coll_name, info, collection_manager)
        count += ans.modified_count
    return count


def _create_update_to_change_username(username, new_username, coll_name, collection_info_field, collection_manager):
    user_filter = _create_user_filter(username, collection_info_field["path"])
    set_username, array_filter = _set_operator_to_change_username(new_username, collection_info_field)
    base_settings = {
        "upsert": False,
    }
    if array_filter:
        base_settings["array_filters"] = [{array_filter: username}]
    return collection_manager.make_update_many(coll_name, user_filter, set_username, base_settings)


def _create_user_filter(username, path):
    return {path: username}


def _set_operator_to_change_username(new_username, collection_information):
    path = _process_path(collection_information)
    operator = "elem"
    pos_operator = _get_filtered_positional_path(path)
    array_filter = ""

    if pos_operator != "-1":
        array_filter = operator + pos_operator
    return {"$set": {path: new_username}}, array_filter


def _process_path(collection_information):
    path = collection_information["path"]
    index_list = collection_information["index_array"]

    if not index_list:
        return path

    field_end_index_list = _get_field_end_index_in_path(path)
    index_list_len = len(index_list)
    index_adjustment = 0
    all_positional_operator = ".$[]"
    for i in range(index_list_len):
        index = index_list[i]
        field_end_index = field_end_index_list[index] + index_adjustment
        if i + 1 == index_list_len:
            path = _add_filtered_positional_operator(path, field_end_index)
        else:
            path = _add_all_positional_operator(path, field_end_index)
            index_adjustment += len(all_positional_operator)
    return path


def _get_field_end_index_in_path(path):
    field_end_index = [m.start() for m in re.finditer("\.", path)]
    field_end_index.append(len(path))
    return field_end_index


def _add_filtered_positional_operator(string, index):
    filtered_positional_operator = ".$[elem]"
    return _add_element_to_string(string, filtered_positional_operator, index)


def _add_all_positional_operator(string, index):
    all_positional_operator = ".$[]"
    return _add_element_to_string(string, all_positional_operator, index)


def _add_element_to_string(string, element, index):
    return string[:index] + element + string[index:]


def _get_filtered_positional_path(string):
    filtered_positional_operator = ".$[elem]"
    operator_index = string.find(filtered_positional_operator)
    if operator_index > 0:
        operator_len = len(filtered_positional_operator)
        return string[operator_index + operator_len:]
    else:
        return "-1"


def _make_user_changes_register(user_initial_info, user_final_info):
    register = {

    }
