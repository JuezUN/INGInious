import os
import web

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException

class UserHintsAPI(APIAuthenticatedPage):

    #Get the content for a hint
    def API_GET(self):

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        username = self.user_manager.session_username()

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        try:
            task = course.get_task(task_id)
        except Exception:
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        if not self.user_manager.course_is_user_registered(course,username):
            raise APIError(400,{"error":"The course does not exists"})

        return 200, self.check_locked_hint_status(self.get_task_hints(task), task_id, username)

    def API_POST(self):

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        username = self.user_manager.session_username()

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        try:
            task = course.get_task(task_id)
        except Exception:
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        if not self.user_manager.course_is_user_registered(course,username):
            raise APIError(400,{"error":"The course does not exists"})

        return 200

    def get_task_hints(self, task):

        hints = task._data

    def check_locked_hint_status(self, hints, task_id, username):

        data = self.database.hints.findOne({"taskid": task_id,
                                                    "username": username})

        to_show_hints_content = []
        allowedHints = data["allowedHints"]
        for hint in allowedHints:
            to_show_hint = {
                "title": 1,
                "penalty": 2,
                "content": None,
                "allowed": False,
                "key": None
            }
            if hint["key"] in hints:
                to_show_hint["content"]
                to_show_hint["allowed"]
                to_show_hints_content.append(to_show_hint)

        return hints
