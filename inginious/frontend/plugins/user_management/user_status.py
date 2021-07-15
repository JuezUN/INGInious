def get_total_open_sessions(username, collection_manager):
    """ return the number of open sessions of a user  """
    sessions = list(collection_manager.make_find_request("sessions", _create_filter_for_sessions(username),
                                                         _create_projection_for_sessions()))
    num_sessions = len(sessions)
    return num_sessions


def get_submissions_running(username, collection_manager):
    """ Returns a list of submissions that are running and belongs to the user """
    return _get_process_running_in_collection(username, "submissions", collection_manager)


def get_custom_test_running(username, collection_manager):
    """ Returns a list of custom test that are running and belongs to the user """
    return _get_process_running_in_collection(username, "custom_tests", collection_manager)


def _create_filter_for_sessions(username):
    """ Returns a dictionary to filter the open sessions of a user in sessions collection """
    return {"data.username": username, "data.loggedin": True}


def _create_projection_for_sessions():
    """  Returns a dictionary to specify what parameters returns from the DB """
    return {"data.loggedin": 1, "_id": 0}


def _get_process_running_in_collection(username, collection_name, collection_manager):
    """ returns a list of process running in collection """
    submissions = list(collection_manager.make_find_request(collection_name, _create_filter_running_jobs(username),
                                                            _create_projection_for_submissions()))
    for submission in submissions:
        submission["_id"] = str(submission["_id"])

    return submissions


def _create_filter_running_jobs(username):
    """ returns a dictionary to filter the user's process that are running """
    return {"username": username, "status": "waiting"}


def _create_projection_for_submissions():
    """ Returns a dictionary to specify what parameters returns from the submissions collection """
    return {"_id": 1, "courseid": 1, "status": 1, "taskid": 1, "submitted_on": 1, "sent_on": 1}
