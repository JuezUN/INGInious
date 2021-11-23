import web

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.common.exceptions import InvalidNameException
from inginious.frontend.plugins.utils import get_mandatory_parameter
from ..user_hint_manager import UserHintManagerSingleton

class HintsModeAPI(AdminApi):

    "API to manage the users hints documents on a task, when task submission mode changes"

    @property
    def user_hint_manager(self) -> UserHintManagerSingleton:
        """ Returns user hint manager singleton """
        return UserHintManagerSingleton.get_instance()

    def get_temporal_task_hints_file_content(self, course, task_id):
        
        temporal_task_file = self.task_factory.get_temporal_task_file(course, task_id)

        temporal_task_file_content = {}

        if temporal_task_file is None:

            self.set_temporal_task_hints_file(course, task_id)
            temporal_task_file_content = self.task_factory.get_temporal_task_file_content(course, task_id)

        return temporal_task_file_content

    def set_temporal_task_hints_file(self, course, task_id):

        data = {}
            
        data["task_hints"] = {}
        data["groups"] = False

        self.task_factory.update_temporal_task_file(course, task_id, data)

    def API_GET(self):
        
        """
            Get task submission mode before it's saved
        """

        input_data = web.input()
        
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')

        course = self.get_course_and_check_rights(course_id)

        use_temporal_file = False
        task = None
        
        try:
            task = self.task_factory.get_task(course, task_id)
            task_data = task._data

        except:
            use_temporal_file = True

        if use_temporal_file:
            try:
                task = self.get_temporal_task_hints_file_content(course, task_id)
                task_data = task.get('data',{})
            except InvalidNameException:
                raise APIError(400, {"error": _("Invalid task name")})
        
        if task is None:
            raise APIError(400, {"error": _("Task does not exist, or task has not been created yet.")})
        
        task_submission_mode = task_data.get('groups', False)

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

        use_temporal_file = False
        task = None
        
        try:
            task = self.task_factory.get_task(course, task_id)
            task_data = task._data

        except:
            use_temporal_file = True

        if use_temporal_file:
            try:
                task = self.get_temporal_task_hints_file_content(course, task_id)
                task_data = task.get('data',{})
            except InvalidNameException:
                raise APIError(400, {"error": _("Invalid task name")})
        
        if task is None:
            raise APIError(400, {"error": _("Task does not exist, or task has not been created yet.")})
        
    
        task_submission_mode = task_data.get('groups', False)
        task_hints = task_data.get('task_hints', {})

        self.task_factory.delete_temporal_task_file(course, task_id)

        try:

            last_submission_mode = ('true' == last_submission_mode)

            if task_submission_mode != last_submission_mode:

                self.user_hint_manager.on_change_task_submission_mode(course_id, task_id, task_submission_mode, task_hints)

        except Exception:
            raise APIError(400, {"error": _("There was a problem to update submission mode on users hints.")})

        return 200, task_submission_mode

