import datetime

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
    course_id = input_dict.get('course_id', None)

    # Generate query
    query_parameters = {}
    if username:
        query_parameters['username'] = username
    if service:
        query_parameters['service'] = _generate_query_for_list(service)
    if course_id:
        query_parameters['course_id'] = _generate_query_for_list(course_id)
    if start_date:
        start_date = datetime.datetime(*map(int, start_date.split('-')))
        query_parameters['date'] = {'$gte': start_date}

    return query_parameters


def _generate_query_for_list(names):
    name_list = names.split(",")
    return {"$in": name_list}
