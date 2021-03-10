from datetime import datetime
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument


class CustomTestManager(object):
    """ Runs custom test job asynchronously """

    def __init__(self, client, user_manager, database):
        self._client = client
        self._user_manager = user_manager
        self._database = database

    def _job_done_callback(self, custom_test_id, result, stdout, stderr):
        custom_test = self.get_custom_test(custom_test_id, False)

        if not custom_test:
            return

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
            Runs a new custom test job asynchronously.
            The general idea works like the SubmissionManager, as it creates a new document in DB to keep track of
            the running custom tests, When the job is done, it calls a callback to update the document in DB to tell
            the frontend the job has finished plus the given results.
            Returns the custom test id.
        """

        if not self._user_manager.session_logged_in():
            raise Exception(_("An user must be logged in to run custom tests"))

        username = self._user_manager.session_username()

        # Prevent student from sending several tests together
        current_custom_test = self._database.custom_tests.find_one({
            "courseid": task.get_course_id(),
            "taskid": task.get_id(),
            "username": username})

        if current_custom_test is not None:
            # This is in case there is a job in DB that was not previously deleted but already finished.
            # Also, in case the current custom test is still in waiting status but the job is there for more than 3
            # minutes because the job probably already finished but the callback was not successfully run.
            current_custom_test_id = str(current_custom_test["_id"])
            if self.is_done(current_custom_test_id) or (
                    self.is_waiting(current_custom_test_id) and self.is_old(current_custom_test)):
                self.delete_custom_test(str(current_custom_test["_id"]))
            else:
                raise Exception(_("A custom test is already pending for this task. Wait for a while to run the tests."))

        job_id = self._client.new_job(task, input_data,
                                      (lambda result, grade, problems, tests, custom, archive, stdout, stderr:
                                       self._job_done_callback(custom_test_id, result, stdout, stderr)),
                                      launcher_name)

        custom_test_obj = {
            "courseid": task.get_course_id(),
            "taskid": task.get_id(),
            "sent_on": datetime.now(),
            "username": username,
            "response_type": task.get_response_type(),
            "status": "waiting",
            "job_id": job_id
        }
        custom_test_id = self._database.custom_tests.insert(custom_test_obj)

        return str(custom_test_id)

    def get_custom_test(self, custom_test_id, user_check=True):
        """ Get a custom test from the database """
        custom_test = self._database.custom_tests.find_one({"_id": ObjectId(custom_test_id)})
        if not custom_test:
            return None
        if user_check and not self.user_is_custom_test_owner(custom_test):
            return None
        return custom_test

    def user_is_custom_test_owner(self, custom_test):
        """ Returns True if the current user is the owner of this custom test, otherwise returns False"""
        if not self._user_manager.session_logged_in():
            raise Exception("An user must be logged in to verify if he owns this custom test")

        return self._user_manager.session_username() == custom_test["username"]

    def delete_custom_test(self, custom_test_id):
        self._database.custom_tests.delete_one({"_id": ObjectId(custom_test_id)})

    def is_waiting(self, custom_test_id, user_check=True):
        """ Tells if a custom test is running/in queue """
        custom_test = self.get_custom_test(custom_test_id, user_check)
        if not custom_test:
            return None
        return custom_test["status"] == "waiting"

    def is_old(self, custom_test):
        """
        Check if the custom test is old. A custom test is considered to be old if this was submitted more than 3 minutes
        ago. This means that the job callback did not update the document in the database.
        """
        if not custom_test:
            return None

        now = datetime.now()
        difference = now - custom_test["sent_on"]
        three_minutes_in_seconds = 3 * 60
        return difference.total_seconds() >= three_minutes_in_seconds

    def is_done(self, custom_test_id, user_check=True):
        """ Tells if a custom test is done and its result is available """
        custom_test = self.get_custom_test(custom_test_id, False)
        if not custom_test:
            return None
        if user_check and not self.user_is_custom_test_owner(custom_test):
            return None
        return custom_test["status"] in {"done", "error"}
