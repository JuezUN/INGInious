import web

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter
from ..user_hint_manager import UserHintManagerSingleton

class HintsModeAPI(AdminApi):

    @property
    def user_hint_manager(self) -> UserHintManagerSingleton:
        """ Returns user hint manager singleton """
        return UserHintManagerSingleton.get_instance()

    def API_GET(self):
        
        """
            Get task submission mode before it's saved
        """

        input_data = web.input()

        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')

        course = self.get_course_and_check_rights(course_id)

        try:
            task = self.task_factory.get_task(course, task_id)
            task_submission_mode = task._data.get('groups')

        except Exception:
            raise APIError(400, {"error": "Task does not exist"})

        return 200, task_submission_mode

    
    def API_POST(self):
        
        """
            Change user hints documents of the task if submission mode has been changed
        """

        input_data = web.input()

        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        last_submission_mode = get_mandatory_parameter(input_data, 'last_submission_mode')

        course = self.get_course_and_check_rights(course_id)

        try:
            task = self.task_factory.get_task(course, task_id)
            task_submission_mode = task._data.get('groups')
            task_hints = task._data.get('task_hints')

            last_submission_mode = ('true' == last_submission_mode)

            if task_submission_mode != last_submission_mode:

                self.user_hint_manager.on_change_task_submission_mode(course_id, task_id, task_submission_mode, task_hints)

        except Exception:
            raise APIError(400, {"error": "There was a problem to update submission mode on user hints"})

        return 200, task_submission_mode

