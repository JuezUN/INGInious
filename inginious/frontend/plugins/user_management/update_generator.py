import datetime
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
    ans = collections_manager.make_update("users", user_filter, new_name, settings)
    return ans.modified_count


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
    ans = collections_manager.make_update("users", user_filter_users, new_email_users, settings)
    return ans.modified_count


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
        count += ans
    return count


def _create_update_to_change_username(username, new_username, coll_name, collection_info_field, collection_manager):
    user_filter = _create_user_filter(username, collection_info_field["path"])
    base_settings = {
        "upsert": False,
    }
    path = _process_path(collection_info_field)

    if is_array(collection_info_field):
        push_new_username = _create_push_operator(path, new_username)
        pull_old_username = _create_pull_operator(path, username)
        there_are_changes = True
        change_username_count = 0
        while there_are_changes:
            push_ans = collection_manager.make_update_many(coll_name, user_filter, push_new_username, base_settings)
            there_are_changes = push_ans.modified_count > 0
            if there_are_changes:
                pull_ans = collection_manager.make_update_many(coll_name, user_filter, pull_old_username, base_settings)
                change_username_count += pull_ans.modified_count
        return change_username_count

    set_username = _set_operator_to_change_username(path, new_username)
    set_ans = collection_manager.make_update_many(coll_name, user_filter, set_username, base_settings)
    return set_ans.modified_count


def _create_push_operator(path, new_username):
    return {"$push": {path: new_username}}


def _create_pull_operator(path, username):
    return {"$pull": {path: username}}


def is_array(collection_information):
    path = collection_information["path"]
    index_list = sorted(collection_information["index_array"])
    if not index_list:
        return False

    num_fields = len(_get_field_end_index_in_path(path))
    last_index_path = num_fields - 1
    return last_index_path == index_list[-1]


def _create_user_filter(username, path):
    return {path: username}


def _set_operator_to_change_username(path, new_username, ):
    return {"$set": {path: new_username}}


def _process_path(collection_information):
    path = collection_information["path"]
    index_list = sorted(collection_information["index_array"])

    if not index_list:
        return path

    field_end_index_list = _get_field_end_index_in_path(path)
    index_list_len = len(index_list)
    index_adjustment = 0
    positional_operator = ".$"
    for i in range(index_list_len):
        index = index_list[i]
        field_end_index = field_end_index_list[index] + index_adjustment
        is_end_string = i + 1 == index_list_len
        if not is_end_string:
            path = _add_positional_operator(path, field_end_index)
            index_adjustment += len(positional_operator)
    return path


def _get_field_end_index_in_path(path):
    field_end_index = [m.start() for m in re.finditer("\.", path)]
    field_end_index.append(len(path))
    return field_end_index


def _add_positional_operator(string, index):
    all_positional_operator = ".$"
    return _add_element_to_string(string, all_positional_operator, index)


def _add_element_to_string(string, element, index):
    return string[:index] + element + string[index:]


def make_user_changes_register(user_original_info, user_final_info, collection_manager):
    date = datetime.datetime.now()
    register = {
        "date": date
    }
    keys = list(user_original_info.keys())
    keys.remove("count")

    for key in keys:
        register["original_" + key] = user_original_info[key]
        register["final_" + key] = user_final_info[key]

    collection_manager.insert_register_user_change(register)
