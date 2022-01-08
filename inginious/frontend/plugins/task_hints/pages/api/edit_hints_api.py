import web

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.exceptions import InvalidNameException

class EditHintsAPI(AdminApi):

    def API_GET(self):

        """
            Get all the data for saved hints in task
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
                task = self.task_factory.get_temporal_task_file_content(course, task_id)
                task_data = task.get('data',{})
            except InvalidNameException:
                raise APIError(400, {"error": _("Invalid task name")})
        
        if task is None:
            raise APIError(400, {"error": _("Task does not exist, or task has not been created yet.")})
        
        task_hints = task_data.get('task_hints', {})

        return 200, {"data": task_hints}
