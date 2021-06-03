from collections import OrderedDict

import web

from inginious.frontend.plugins.user_management.find_generator import get_num_open_user_sessions, \
    get_submissions_running, \
    get_custom_test_running
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton


class UserStatusAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        username = get_mandatory_parameter(web.input(), "username")
        collection_manager = CollectionsManagerSingleton.get_instance()

        user_status = {"username": username,
                       "num_connections": get_num_open_user_sessions(username, collection_manager)}
        submissions = get_submissions_running(username, collection_manager)
        custom_test = get_custom_test_running(username, collection_manager)

        self.config_submissions(submissions)
        self.config_submissions(custom_test)

        user_status["submissions"] = sorted(submissions, key=lambda k: (k["courseid"], k["taskid"]))
        user_status["custom_test"] = sorted(custom_test, key=lambda k: (k["courseid"], k["taskid"]))

        return 200, user_status

    def config_submissions(self, submissions):
        lang = self.user_manager.session_language()
        for submission in submissions:
            course_name = self.course_factory.get_course(submission["courseid"]).get_name(lang)
            submission["taskid"] = self.course_factory.get_task(submission["courseid"],
                                                                submission["taskid"]). \
                get_name_or_id(lang)
            submission["courseid"] = course_name if course_name else submission["courseid"]

            if "submitted_on" in submission:
                submission["submitted_on"] = submission["submitted_on"].strftime("%d/%m/%Y, %H:%M:%S")
            else:
                submission["submitted_on"] = submission["sent_on"].strftime("%d/%m/%Y, %H:%M:%S")
                del submission["sent_on"]
