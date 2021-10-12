import web

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.plugins.utils.admin_api import AdminApi
from inginious.frontend.plugins.utils import get_mandatory_parameter


class EditHintsAPI(AdminApi):

    def API_GET(self):

        """
            Get all the data for saved hints in task
        """

        input_data = web.input()

        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')

        course = self.get_course_and_check_rights(course_id)

        try:
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": "Task does not exist, or task has not been created yet."})

        task_hints = task._data.get('task_hints', {})

        return 200, {"data": task_hints}
