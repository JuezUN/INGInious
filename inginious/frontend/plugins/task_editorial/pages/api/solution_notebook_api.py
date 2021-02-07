import os
import web

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.common.course_factory import CourseNotFoundException, CourseUnreadableException, InvalidNameException
from inginious.frontend.plugins.utils import get_mandatory_parameter

class SolutionNotebookApi(APIAuthenticatedPage):

    def API_GET(self):

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        notebook_name = get_mandatory_parameter(input_data, 'notebook_name')

        try:
            course = self.course_factory.get_course(course_id)
        except (CourseNotFoundException, InvalidNameException, CourseUnreadableException):
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        try:
            task = course.get_task(task_id)
        except Exception:
            raise APIError(400, {"error": "The task does not exist in the course"})

        try:
            with open(os.path.join(task.get_fs().prefix, notebook_name), 'r') as notebook_file:
                return 200, notebook_file.read()
        except Exception:
            return 200, ""

