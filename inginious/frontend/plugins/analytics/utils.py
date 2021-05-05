import datetime
import inginious.frontend.pages.api._api_page as api

_use_minfied = True


def set_use_minified(value):
    global _use_minfied
    _use_minfied = value


def use_minified():
    return _use_minfied


def get_api_query_parameters(input_dict):
    username = input_dict.get('username', None)
    service = input_dict.get('service', None)
    start_date = input_dict.get('start_date', None)
    end_date = input_dict.get('end_date', None)
    course_id = input_dict.get('course_id', None)

    # Generate query
    query_parameters = {}
    if username:
        query_parameters['username'] = username
    if service:
        query_parameters['service'] = _parse_list_for_query(service)
    if course_id:
        query_parameters['course_id'] = _parse_list_for_query(course_id)

    if start_date or end_date:
        query_parameters['date'] = {}
        if start_date:
            start_date = _convert_string_to_date(start_date)
            query_parameters['date']['$gte'] = start_date
        if end_date:
            end_date = _convert_string_to_date(end_date)
            query_parameters['date']['$lte'] = end_date.replace(hour=23, minute=59, second=59)
        if start_date and end_date and (end_date < start_date):
            raise api.APIError(400, _("The start date must be greater than end date."))

    return query_parameters


def _parse_list_for_query(names):
    """ return a dict to be used to filter data by a list of names """
    name_list = names.split(",")
    if "none" in name_list:
        name_list[name_list.index("none")] = None
    return {"$in": name_list}


def _convert_string_to_date(string_date):
    """ Convert a string in datetime object """
    try:
        return datetime.datetime(*map(int, string_date.split('-')))
    except (ValueError, TypeError):
        raise api.APIError(400, _("Invalid date format"))


def get_dictionary_value(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    else:
        return None
