from collections import OrderedDict

from inginious.frontend.plugins.user_management.utils import get_collection_document


def get_count_username_occurrences(username, collection_manager):
    collection_name_list = collection_manager.get_collections_names()
    dictionary = _create_occurrences_dict(collection_name_list)
    collection_information = get_collection_document()
    to_remove = []

    def get_aggregation_result(name, query):
        ans = collection_manager.make_aggregation(name, query)
        return ans[0]["num_appearances"] if ans else 0

    for collection_name in collection_name_list:
        if collection_name in collection_information:
            collection_info = collection_information[collection_name]
            if collection_info[0]["path"] != "none":
                aggregation = _create_aggregation_to_count(username, collection_info)
                dictionary[collection_name] = get_aggregation_result(collection_name, aggregation)
            else:
                to_remove.append(collection_name)
        else:
            has_username = has_username_key(collection_manager.get_all_key_names(collection_name))
            if has_username:
                aggregation = _create_aggregation_to_count(username, [{"path": "username"}])
                dictionary[collection_name] = get_aggregation_result(collection_name, aggregation)

    for item_to_remove in to_remove:
        del dictionary[item_to_remove]
    return OrderedDict(sorted(dictionary.items()))


def _create_occurrences_dict(collection_names):
    return OrderedDict.fromkeys(collection_names, 0)


def has_username_key(collection_keys):
    return "username" in collection_keys


def _create_aggregation_to_count(username, information):
    parameter_names_dict, parameter_names = _generate_new_names(information)

    query = [
        _create_match_pipeline(username, information),
        _replace_parameters_names(parameter_names_dict, parameter_names),
        _put_all_parameters_in_arrays(parameter_names),
        _reduce_all_mongo_array(parameter_names_dict, information),
        _count_username_occurrences(username, parameter_names),
        _project_sum(parameter_names)
    ]

    return query


def _generate_new_names(information):
    key_name_in_json = "path"
    new_names_bidirectional_dict = {}
    parameter_names = []
    i = 0
    for info in information:
        new_name = "v" + str(i)
        path = info[key_name_in_json]

        new_names_bidirectional_dict[new_name] = path
        new_names_bidirectional_dict[path] = new_name
        parameter_names.append(new_name)

        i += 1
    return new_names_bidirectional_dict, parameter_names


def _create_match_pipeline(username, information):
    key_name_in_json = "path"
    match_content = []
    for info in information:
        dictionary = {info[key_name_in_json]: username}
        match_content.append(dictionary)

    match = {
        "$match": {"$or": match_content}
    }
    return match


def _replace_parameters_names(parameter_names_dict, parameter_names):
    project_dict = {}

    for parameter in parameter_names:
        project_dict[parameter] = "$" + parameter_names_dict[parameter]

    return {"$project": project_dict}


def _put_all_parameters_in_arrays(parameter_names):
    group_dict = {
        "_id": None
    }
    for parameter in parameter_names:
        group_dict[parameter] = _push_parameter_to_mongo_array(parameter)

    return {"$group": group_dict}


def _push_parameter_to_mongo_array(parameter):
    return {"$push": "$" + parameter}


def _reduce_all_mongo_array(parameter_names_dict, information):
    project_dict = {}
    type_name_in_json_file = "array_dimension"
    key_name_in_json = "path"
    value_to_keep_parameter = 1

    for info in information:
        num_dimensions = info[type_name_in_json_file]
        path = info[key_name_in_json]
        parameter = parameter_names_dict[path]
        if num_dimensions > 0:
            project_dict[parameter] = _reduce_mongo_array(parameter, num_dimensions)
        else:
            project_dict[parameter] = value_to_keep_parameter

    return {"$project": project_dict}


def _reduce_mongo_array(parameter, num_dimensions):
    reduce_dict = {
        "input": "$" + parameter,
        "initialValue": [],
        "in": _multi_concat_array(num_dimensions)
    }
    return {"$reduce": reduce_dict}


def _multi_concat_array(num_dimensions):
    if num_dimensions < 2:
        return {"$concatArrays": ["$$value", "$$this"]}
    else:
        return {"$concatArrays": ["$$value", _reduce_mongo_array("$this", num_dimensions - 1)]}


def _count_username_occurrences(username, parameter_names):
    project_dict = {}
    for parameter in parameter_names:
        parameter_filter = _filter_array_by_username(username, parameter)
        project_dict[parameter] = _get_size_mongo_array(parameter_filter)
    return {"$project": project_dict}


def _get_size_mongo_array(mongo_array):
    return {"$size": mongo_array}


def _filter_array_by_username(username, parameter):
    filter_dict = {
        "input": "$" + parameter,
        "as": "item",
        "cond": {
            "$eq": ["$$item", username]
        }
    }
    return {"$filter": filter_dict}


def _project_sum(parameter_names):
    parameter_names = ["$" + parameter for parameter in parameter_names]
    return {"$project": {"num_appearances": {"$sum": parameter_names}}}
