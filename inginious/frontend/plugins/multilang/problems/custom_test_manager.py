from datetime import datetime
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument


class CustomTestManager(object):
    """ Runs job asynchronously """

    def __init__(self, client, user_manager, database):
        self._client = client
        self._user_manager = user_manager
        self._database = database

    def _job_done_callback(self, custom_test_id, task, result, stdout, stderr):
        custom_test = self.get_custom_test(custom_test_id, False)

        data = {
            "status": ("done" if result[0] == "success" or result[0] == "failed" else "error"),
            "result": result[0],
            "text": result[1],
            "stdout": stdout,
            "stderr": stderr
        }

        unset_obj = {
            "job_id": "",
        }

        self._database.custom_tests.find_one_and_update(
            {"_id": custom_test["_id"]},
            {"$set": data, "$unset": unset_obj},
            return_document=ReturnDocument.AFTER
        )

    def new_job(self, task, input_data, launcher_name="Unknown"):
        """
            Runs a new job.
            It works exactly like the Client class, instead that there is no callback and directly returns result,
            in the form of a tuple (result, grade, problems, tests, custom, archive).
        """

        if not self._user_manager.session_logged_in():
            raise Exception(_("A user must be logged in to submit an object"))

        username = self._user_manager.session_username()

        # Prevent student from sending several tests together
        current_custom_test = self._database.custom_tests.find_one({
            "courseid": task.get_course_id(),
            "taskid": task.get_id(),
            "username": username})

        if current_custom_test is not None:
            # This is in case there is a job in DB that was not previously deleted but already finished.
            # Also, in case the current custom test is still in waiting status but the job in not in the queue.
            if current_custom_test["status"] in {"done", "error"} or \
                    not self.is_job_in_queue(current_custom_test["job_id"]):
                self.delete_custom_test(str(current_custom_test["_id"]))
            else:
                raise Exception(_("A custom test is already pending for this task!"))

        job_id = self._client.new_job(task, input_data,
                                      (lambda result, grade, problems, tests, custom, archive, stdout, stderr:
                                       self._job_done_callback(custom_test_id, task, result, stdout, stderr)),
                                      launcher_name)

        custom_test_obj = {
            "courseid": task.get_course_id(),
            "taskid": task.get_id(),
            "sent_on": datetime.now(),
            "username": [username],
            "response_type": task.get_response_type(),
            "status": "waiting",
            "job_id": job_id
        }
        custom_test_id = self._database.custom_tests.insert(custom_test_obj)

        return str(custom_test_id)

    def get_custom_test(self, custom_test_id, user_check=True):
        """ Get a submission from the database """
        custom_test = self._database.custom_tests.find_one({'_id': ObjectId(custom_test_id)})
        if user_check and not self.user_is_custom_test_owner(custom_test):
            return None
        return custom_test

    def user_is_custom_test_owner(self, custom_test):
        """ Returns true if the current user is the owner of this jobid, false else """
        if not self._user_manager.session_logged_in():
            raise Exception("A user must be logged in to verify if he owns a jobid")

        return self._user_manager.session_username() in custom_test["username"]

    def delete_custom_test(self, custom_test_id):
        self._database.custom_tests.delete_one({'_id': ObjectId(custom_test_id)})

    def is_running(self, custom_test_id, user_check=True):
        """ Tells if a submission is running/in queue """
        custom_test = self.get_custom_test(custom_test_id, user_check)
        return custom_test["status"] == "waiting"

    def is_done(self, custom_test_id, user_check=True):
        """ Tells if a submission is done and its result is available """
        custom_test = self.get_custom_test(custom_test_id, False)
        if user_check and not self.user_is_custom_test_owner(custom_test):
            return None
        return custom_test["status"] == "done" or custom_test["status"] == "error"

    def get_job_queue_snapshot(self):
        """ Get a snapshot of the remote backend job queue. May be a cached version.
            May not contain recent jobs. May return None if no snapshot is available

        Return a tuple of two lists (None, None):
        jobs_running: a list of tuples in the form
            (job_id, is_current_client_job, info, launcher, started_at, max_end)
            where
            - job_id is a job id. It may be from another client.
            - is_current_client_job is a boolean indicating if the client that asked the request has started the job
            - agent_name is the agent name
            - info is "courseid/taskid"
            - launcher is the name of the launcher, which may be anything
            - started_at the time (in seconds since UNIX epoch) at which the job started
            - max_end the time at which the job will timeout (in seconds since UNIX epoch), or -1 if no timeout is set
        jobs_waiting: a list of tuples in the form
            (job_id, is_current_client_job, info, launcher, max_time)
            where
            - job_id is a job id. It may be from another client.
            - is_current_client_job is a boolean indicating if the client that asked the request has started the job
            - info is "courseid/taskid"
            - launcher is the name of the launcher, which may be anything
            - max_time the maximum time that can be used, or -1 if no timeout is set
        """
        return self._client.get_job_queue_snapshot()

    def is_job_in_queue(self, job_id):
        jobs_queue = self.get_job_queue_snapshot()

        running_job_ids = set(map(lambda job: job[0], jobs_queue[0]))
        waiting_job_ids = set(map(lambda job: job[0], jobs_queue[1]))

        return job_id in running_job_ids or job_id in waiting_job_ids
