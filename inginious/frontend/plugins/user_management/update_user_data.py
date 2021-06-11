import datetime
from inginious.frontend.plugins.user_management.utils import get_collection_document
import re


def make_user_changes_register(user_original_info, user_final_info, collections_manager):
    """ create a register about the changes of a user """
    date = datetime.datetime.now()
    register = {
        "date": date
    }
    keys = list(user_original_info.keys())
    keys.remove("count")

    for key in keys:
        register["original_" + key] = user_original_info[key]
        register["final_" + key] = user_final_info[key]

    collections_manager.insert_register_user_change(register)


def change_name(username, param, collection_manager):
    """ change the name of a user """
    user_filter = {
        "username": username
    }
    new_name = {
        "$set": {"realname": param}
    }
    ans = collection_manager.update_collection("users", user_filter, new_name)
    return ans.modified_count


def change_email(username, param, collections_manager):
    """ change the email of a user """
    user_filter_users = {
        "username": username
    }
    new_email_users = {
        "$set": {"email": param}
    }

    ans = collections_manager.update_collection("users", user_filter_users, new_email_users)
    return ans.modified_count


def change_username(username, new_username, collection_manager, collection_name_list):
    """ change the username of a user """
    collection_information_list = get_collection_document()
    default_collection_information = [{"path": "username", "index_array": []}]
    count = 0
    for collection_name in collection_name_list:
        if collection_name in collection_information_list:
            information = collection_information_list[collection_name]
        else:
            information = default_collection_information  # TODO: array?
        count += _crete_update_to_change_username_collection(username, new_username, collection_name, information,
                                                             collection_manager)
    return count


def close_user_sessions(username, collection_manager):
    """ Close the open sessions of a user """
    update_filter = {
        "data.username": username
    }
    close_sessions = {
        "$set": {
            "data.loggedin": False
        }
    }

    return collection_manager.update_many_in_collection("sessions", update_filter, close_sessions)


def add_block_user(username, collection_manager):
    """ Add the field block to a user's document in users collection to indicate that the user can't do logging"""
    user_filter = {
        "username": username
    }
    new_name = {
        "$set": {"block": True}
    }

    return collection_manager.update_collection("users", user_filter, new_name)


def remove_block_user(username, collection_manager):
    """ Removes the block field from the user's document """
    user_filter = {
        "username": username
    }
    new_name = {
        "$unset": {"block": ""}
    }

    return collection_manager.update_collection("users", user_filter, new_name)


def is_array(collection_information):
    """ return a boolean value to determinate if the field that is contents the username is an array """
    path = collection_information["path"]
    index_list = sorted(collection_information["index_array"])
    if not index_list:
        return False

    num_fields = len(_get_field_end_index_in_path(path))
    last_index_path = num_fields - 1
    return last_index_path == index_list[-1]


def _crete_update_to_change_username_collection(username, new_username, coll_name, collection_info, collection_manager):
    """ For each sub set of information about a collection (path and index_array), make a update process
    and count the number of changes.
     """
    count = 0
    for info in collection_info:
        ans = _create_update_to_change_username(username, new_username, coll_name, info, collection_manager)
        count += ans
    return count


def _create_update_to_change_username(username, new_username, coll_name, collection_info_field, collection_manager):
    """ update the username with the new username in a specific path """
    user_filter = _create_user_filter(username, collection_info_field["path"])
    path = _process_path(collection_info_field)

    if is_array(collection_info_field):
        push_new_username = _create_push_operator(path, new_username)
        pull_old_username = _create_pull_operator(path, username)
        there_are_changes = True
        change_username_count = 0
        while there_are_changes:
            push_ans = collection_manager.update_many_in_collection(coll_name, user_filter, push_new_username)
            there_are_changes = push_ans.modified_count > 0
            if there_are_changes:
                pull_ans = collection_manager.update_many_in_collection(coll_name, user_filter, pull_old_username)
                change_username_count += pull_ans.modified_count
        return change_username_count
    # TODO IF it has arrays
    set_username = _set_operator_to_change_username(path, new_username)
    set_ans = collection_manager.update_many_in_collection(coll_name, user_filter, set_username)
    return set_ans.modified_count


def _create_push_operator(path, new_username):
    """ create a push pipeline to insert the new username in a mongodb array """
    return {"$push": {path: new_username}}


def _create_pull_operator(path, username):
    """ create a pull pipeline to remove the old username in a mongodb array """
    return {"$pull": {path: username}}


def _create_user_filter(username, path):
    """ returns a dictionary to filter the collection by the username """
    return {path: username}


def _set_operator_to_change_username(path, new_username):
    """ returns a dictionary to determinate what field has to change """
    return {"$set": {path: new_username}}


def _process_path(collection_information):
    """ returns the path that will be used in the update process """
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
    """ return a list with the indexes of the ends of the fields in a path
    e.g: for the path  data.user the list will be [4,9].
    """
    field_end_index = [m.start() for m in re.finditer("\.", path)]
    field_end_index.append(len(path))
    return field_end_index


def _add_positional_operator(string, index):
    """ add the positional operator to a string """
    positional_operator = ".$"
    return _add_element_to_string(string, positional_operator, index)


def _add_element_to_string(string, string_to_insert, index):
    """ Insert a string in the indicated index of a string  """
    return string[:index] + string_to_insert + string[index:]
