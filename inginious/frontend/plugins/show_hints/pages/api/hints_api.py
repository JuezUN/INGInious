import os
import web

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException
from ..user_hints import UserHint

class UserHintsAPI(APIAuthenticatedPage):

    # Get the content for a hint
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
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        if not self.user_manager.course_is_user_registered(course,username):
            raise APIError(400,{"error":"The course does not exists"})

        userhint = UserHint(username, task_id, self.database)
        return 200, userhint.check_locked_hint_status(self.get_task_hints(task))

    # Set a hint to a user in database to "unlock" it
    def API_POST(self):

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        username = self.user_manager.session_username()
        hint_id = get_mandatory_parameter(input_data, 'hint_id')

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        try:
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": "The course does not exists or the user does not have permissions"})

        if not self.user_manager.course_is_user_registered(course,username):
            raise APIError(400,{"error":"The course does not exists"})

        task_hints = self.get_task_hints(task)

        try:
            userhint = UserHint(username, task_id, self.database)
            userhint.add_hint_on_allowed(hint_id, task_hints)
        except Exception:
            return 200, {"status":"error","message":"An error ocurred when update hint status"}

        return 200, {"status":"success","message":"Unlocked list updated successfully (Penalty was applied)"}

    def get_task_hints(self, task):

        """ Method to get the task hints """
        hints = task._data.get("task_hints", [])
        return hints
