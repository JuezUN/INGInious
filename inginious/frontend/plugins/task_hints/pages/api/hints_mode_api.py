import web

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.common.task_file_readers.yaml_reader import TaskYAMLFileReader
from inginious.frontend.plugins.utils import get_mandatory_parameter
from ..user_hint_manager import UserHintManagerSingleton

class HintsModeAPI(AdminApi):

    "API to manage the users hints documents on a task, when task submission mode changes"

    @property
    def user_hint_manager(self) -> UserHintManagerSingleton:
        """ Returns user hint manager singleton """
        return UserHintManagerSingleton.get_instance()

    def get_temporal_task_hints_file(self, course, task_id):
        
        temporal_task_file = self.task_factory.get_temporal_task_file(course, task_id)
        task_file_manager = TaskYAMLFileReader()

        if not temporal_task_file:

            data = {}
            
            data["task_hints"] = {}
            data["groups"] = False

            temporal_task_file_content = task_file_manager.dump(data)

            temporal_task_file = self.task_factory.get_task_fs(course.get_id(), task_id).put("task_temp.yaml", temporal_task_file_content)
            temporal_task_file = self.task_factory.get_task_fs(course.get_id(), task_id).get("task_temp.yaml")

        return task_file_manager.load(temporal_task_file)


    def API_GET(self):
        
        """
            Get task submission mode before it's saved
        """

        input_data = web.input()

        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')

        course = self.get_course_and_check_rights(course_id)

        try:
            task_file = self.task_factory.get_task(course, task_id)
            task_submission_mode = task_file._data.get('groups', False)

        except Exception:
            #raise APIError(400, {"error": _("Task does not exist, or task has not been created yet.")})
            task_file = self.get_temporal_task_hints_file(course, task_id)
            task_submission_mode = task_file.get('groups', False)

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
        except Exception:
            raise APIError(400, {"error": _("Task does not exist, or task has not been created yet.")})

        try:
            task_submission_mode = task._data.get('groups', False)
            task_hints = task._data.get('task_hints', {})

            last_submission_mode = ('true' == last_submission_mode)

            if task_submission_mode != last_submission_mode:

                self.user_hint_manager.on_change_task_submission_mode(course_id, task_id, task_submission_mode, task_hints)

        except Exception:
            raise APIError(400, {"error": _("There was a problem to update submission mode on users hints.")})

        return 200, task_submission_mode

