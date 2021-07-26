import os
import web
import yaml

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.common.course_factory import CourseNotFoundException, CourseUnreadableException, InvalidNameException
from inginious.frontend.plugins.utils import get_mandatory_parameter


class TaskCodePreviewAPI(APIAuthenticatedPage):
    """
    API to get the code template associated to a language and a given task.
    """

    def API_GET(self):
        # Validate parameters
        username = self.user_manager.session_username()
        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, "course_id")
        task_id = get_mandatory_parameter(input_data, "task_id")
        language = get_mandatory_parameter(input_data, "language")

        try:
            course = self.course_factory.get_course(course_id)
        except (CourseNotFoundException, InvalidNameException, CourseUnreadableException):
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        if not self.user_manager.course_is_user_registered(course, username):
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        try:
            task = course.get_task(task_id)
        except Exception:
            raise APIError(400, {"error": "The task does not exist in the course"})

        try:
            with open(os.path.join(task.get_fs().prefix, 'task.yaml'), 'r') as task_yaml:
                try:
                    data = yaml.safe_load(task_yaml)
                    filename = data['code_preview_pairs'][language]
                    with open(os.path.join(task.get_fs().prefix, filename), 'r') as file_preview:
                        return 200, file_preview.read()
                except yaml.YAMLError as exc:
                    return 200, ""
        except Exception:
            return 200, ""
