import json
import os
import web

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException


class EditHintsAPI(APIAuthenticatedPage):

    def API_GET(self):

        """
            Get all the data for saved hints in task
        """

        input_data = web.input()

        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": "The course does not exist or the user does not have permissions"})

        try:
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": "The task does not exist in the course"})

        task_hints = task._data.get('task_hints', {})

        return 200, {"data": task_hints}
