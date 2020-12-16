import os
import web
import yaml

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.common.course_factory import CourseNotFoundException, CourseUnreadableException, InvalidNameException


class TaskPreviewFileAPI(APIAuthenticatedPage):
    def API_GET(self):
        # Validate parameters
        username = self.user_manager.session_username()
        course_id = web.input(course_id=None).course_id
        task_id = web.input(task_id=None).task_id
        language = web.input(language=None).language
        if course_id is None:
            raise APIError(400, {"error": "course_id is mandatory"})
        if task_id is None:
            raise APIError(400, {"error": "task_id is mandatory"})
        if language is None:
            raise APIError(400, {"error": "language is mandatory"})

        try:
            course = self.course_factory.get_course(course_id)
        except (CourseNotFoundException, InvalidNameException, CourseUnreadableException):
            raise APIError(400, {"error", "The course does not exists or the user does not have permissions"})

        if not self.user_manager.course_is_user_registered(course, username):
            raise APIError(400, {"error", "The course does not exists or the user does not have permissions"})

        try:
            task = course.get_task(task_id)
        except:
            raise APIError(400, {"error", "The task does not exist in the course"})

        try:
            with open(os.path.join(task.get_fs().prefix, 'task.yaml'), 'r') as task_yaml:
                try:
                    data = yaml.safe_load(task_yaml)
                    filename = data['code_preview_pairs'][language]
                    with open(os.path.join(task.get_fs().prefix, filename), 'r') as file_preview:
                        return 200, file_preview.read()
                except yaml.YAMLError as exc:
                    print(exc)
                    return 200, ""
        except:
            return 200, ""
