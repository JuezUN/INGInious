from collections import OrderedDict

from inginious.frontend.plugins.user_management.utils import get_collection_document


def search_user(user_text, collections_manager, field=None):
    """ returns a list of users matching the search parameter.
    :param user_text: Is a mongodb regular expresion
    :param collections_manager: Is the singleton class
    :param field: Is an optional parameter to indicate by which specific field to filter. By default, it filter for all
    field_names
     """

    def get_regex_pipeline(field_name):
        return {field_name: {"$regex": user_text}}

    field_names = ["username", "email"]
    or_pipeline = []

    if field in field_names:
        or_pipeline.append(get_regex_pipeline(field))
    else:
        or_pipeline = [get_regex_pipeline(field_name) for field_name in field_names]

    user_filter = {
        "$match": {
            "$or": or_pipeline
        }}
    projection = {"$project": {"_id": 0, "username": 1, "realname": 1, "email": 1
                               }
                  }
    query = [user_filter, projection]

    return list(collections_manager.make_aggregation("users", query))


def get_count_username_occurrences(username, collection_manager):
    """ returns a dictionary with the collections names as key and the number username occurrences
    in the collection as value """
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
            # TODO: message to indicate that there is not info about the collection. Try to know if is a list. Type
            has_username = has_username_key(collection_manager.get_all_key_names(collection_name))
            if has_username:
                aggregation = _create_aggregation_to_count(username, [{"path": "username"}])
                dictionary[collection_name] = get_aggregation_result(collection_name, aggregation)

    for item_to_remove in to_remove:
        del dictionary[item_to_remove]
    return OrderedDict(sorted(dictionary.items()))


def _create_occurrences_dict(collection_names):
    """ create the dictionary of occurrences with all the collection names and 0 as value"""
    return OrderedDict.fromkeys(collection_names, 0)


def has_username_key(collection_keys):
    """ returns a boolean value to determinate if username is in a collection """
    return "username" in collection_keys


def _create_aggregation_to_count(username, information):
    """ returns a list with the pipelines to be process and get the occurrences count """
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
    """ generates the new names whom replace the paths in the aggregation """
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
    """ create the match pipeline """
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
    """ create a pipeline to replace the path with new names in the aggregation """
    project_dict = {}

    for parameter in parameter_names:
        project_dict[parameter] = "$" + parameter_names_dict[parameter]

    return {"$project": project_dict}


def _put_all_parameters_in_arrays(parameter_names):
    """ make a pipeline to group the results in arrays """
    group_dict = {
        "_id": None
    }
    for parameter in parameter_names:
        group_dict[parameter] = _push_parameter_to_mongo_array(parameter)

    return {"$group": group_dict}


def _push_parameter_to_mongo_array(parameter):
    """ returns the pipeline that put values in an array """
    return {"$push": "$" + parameter}


def _reduce_all_mongo_array(parameter_names_dict, information):
    """ create a pipeline that turn each mongodb array to one dimension """
    project_dict = {}
    type_name_in_json_file = "index_array"
    key_name_in_json = "path"
    value_to_keep_parameter = 1

    for info in information:
        num_dimensions = len(info[type_name_in_json_file])
        path = info[key_name_in_json]
        parameter = parameter_names_dict[path]
        if num_dimensions > 0:
            project_dict[parameter] = _reduce_mongo_array(parameter, num_dimensions)
        else:
            project_dict[parameter] = value_to_keep_parameter

    return {"$project": project_dict}


def _reduce_mongo_array(parameter, num_dimensions):
    """ pipeline to reduce an array to one dimensions  """
    reduce_dict = {
        "input": "$" + parameter,
        "initialValue": [],
        "in": _multi_concat_array(num_dimensions)
    }
    return {"$reduce": reduce_dict}


def _multi_concat_array(num_dimensions):
    """ pipeline to concat internal arrays """
    if num_dimensions < 2:
        return {"$concatArrays": ["$$value", "$$this"]}
    else:
        return {"$concatArrays": ["$$value", _reduce_mongo_array("$this", num_dimensions - 1)]}


def _count_username_occurrences(username, parameter_names):
    """ get the the len of all the mongodb arrays """
    project_dict = {}
    for parameter in parameter_names:
        parameter_filter = _filter_array_by_username(username, parameter)
        project_dict[parameter] = _get_size_mongo_array(parameter_filter)
    return {"$project": project_dict}


def _get_size_mongo_array(mongo_array):
    """ pipeline to get the len of a mongo array """
    return {"$size": mongo_array}


def _filter_array_by_username(username, parameter):
    """ pipeline to only keep the usernames equal to the username parameter"""
    filter_dict = {
        "input": "$" + parameter,
        "as": "item",
        "cond": {
            "$eq": ["$$item", username]
        }
    }
    return {"$filter": filter_dict}


def _project_sum(parameter_names):
    """ pipeline to get the sum of the array lens """
    parameter_names = ["$" + parameter for parameter in parameter_names]
    return {"$project": {"num_appearances": {"$sum": parameter_names}}}
