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
        query_parameters['service'] = _generate_query_for_list(service)
    if course_id:
        query_parameters['course_id'] = _generate_query_for_list(course_id)

    if start_date or end_date:
        query_parameters['date'] = {}
        if start_date:
            query_parameters['date']['$gte'] = _convert_string_to_date(start_date)
        if end_date:
            query_parameters['date']['$lte'] = _convert_string_to_date(end_date)

    return query_parameters


def _generate_query_for_list(names):
    name_list = names.split(",")
    return {"$in": name_list}


def _convert_string_to_date(string_date):
    try:
        return datetime.datetime(*map(int, string_date.split('-')))
    except (ValueError, TypeError):
        raise api.APIError(400, "Invalid date format")
