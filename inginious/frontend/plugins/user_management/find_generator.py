def get_num_open_user_sessions(username, collection_manager):
    sessions = list(collection_manager.make_find_request("sessions", _create_filter_for_sessions(username),
                                                         _create_projection_for_sessions()))
    num_sessions = len(sessions)
    return num_sessions


def _create_filter_for_sessions(username):
    return {"data.username": username}


def _create_projection_for_sessions():
    return {"data.loggedin": 1, "_id": 0}


def get_submissions_running(username, collection_manager):
    return _get_submissions_running_in_collection(username, "submissions", collection_manager)


def get_custom_test_running(username, collection_manager):
    return _get_submissions_running_in_collection(username, "custom_tests", collection_manager)


def _get_submissions_running_in_collection(username, collection_name, collection_manager):
    submissions = list(collection_manager.make_find_request(collection_name, _create_filter_for_submissions(username),
                                                            _create_projection_for_submissions()))
    for submission in submissions:
        submission["_id"] = str(submission["_id"])

    return submissions


def _create_filter_for_submissions(username):
    return {"username": username, "status": "waiting"}


def _create_projection_for_submissions():
    return {"_id": 1, "courseid": 1, "status": 1, "taskid": 1, "submitted_on": 1}
