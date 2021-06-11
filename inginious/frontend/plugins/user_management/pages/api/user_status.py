import web

from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.user_management.user_status import get_num_open_user_sessions, \
    get_submissions_running, get_custom_test_running
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class UserStatusAPI(SuperadminAPI):
    """ API to know the process that are running of a user """

    def API_GET(self):
        """ ger request. returns a list of the process that the user is running"""
        self.check_superadmin_rights()
        username = get_mandatory_parameter(web.input(), "username")
        collection_manager = CollectionsManagerSingleton.get_instance()

        user_status = {"username": username,
                       "num_connections": get_num_open_user_sessions(username, collection_manager)}
        submissions = get_submissions_running(username, collection_manager)
        custom_test = get_custom_test_running(username, collection_manager)

        self.config_processes_dict(submissions)
        self.config_processes_dict(custom_test)

        user_status["submissions"] = sorted(submissions, key=lambda k: (k["courseid"], k["taskid"]))
        user_status["custom_test"] = sorted(custom_test, key=lambda k: (k["courseid"], k["taskid"]))

        return 200, user_status

    def config_processes_dict(self, processes):
        """ This method apply a "format" to the process, get course name,
        get the task name and apply a format for the date """
        lang = self.user_manager.session_language()
        for process in processes:
            course_name = self.course_factory.get_course(process["courseid"]).get_name(lang)
            process["taskid"] = self.course_factory.get_task(process["courseid"],
                                                             process["taskid"]). \
                get_name_or_id(lang)
            process["courseid"] = course_name if course_name else process["courseid"]

            if "submitted_on" in process:
                process["submitted_on"] = process["submitted_on"].strftime("%d/%m/%Y, %H:%M:%S")
            else:
                process["submitted_on"] = process["sent_on"].strftime("%d/%m/%Y, %H:%M:%S")
                del process["sent_on"]
