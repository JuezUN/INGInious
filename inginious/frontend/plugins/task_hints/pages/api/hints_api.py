import os
import web

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException
from ..user_hint_manager import UserHintManager

class UserHintsAPI(APIAuthenticatedPage):

    def API_GET(self):

        """ Get the content for a hint """

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        username = self.user_manager.session_username()

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": _("The course does not exists or the user does not have permissions.")})

        try:
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": _("The task does not exist in the course.")})

        if not self.user_manager.course_is_user_registered(course,username):
            raise APIError(400,{"error": _("The user is not registered in this course.")})

        allowed_hints_list = {}

        try:
            user_hint_manager = UserHintManager(username, task_id, self.database)
            allowed_hints_list = user_hint_manager.check_locked_hint_status(self.get_task_hints(task))
        except Exception:
            raise  APIError(400,{"message": _("An error occurred while getting the user's hints.")})

        return 200, {"status": "success","data": allowed_hints_list}

    def API_POST(self):

        """ Set a hint to a user in database to "unlock" it """

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        username = self.user_manager.session_username()
        hint_id = get_mandatory_parameter(input_data, 'hint_id')

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": _("The course does not exists or the user does not have permissions.")})

        try:
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": _("The task does not exist in the course.")})

        if not self.user_manager.course_is_user_registered(course,username):
            raise APIError(400,{"error": _("The user is not registered in this course.")})

        task_hints = self.get_task_hints(task)

        try:
            user_hint_manager = UserHintManager(username, task_id, self.database)
            total_penalty = user_hint_manager.add_hint_on_allowed(hint_id, task_hints)
        except Exception:
            return 200, {"status":"error","message": _("An error occurred while updating status of the hint.")}

        return 200, {"status":"success","message": _("Hint unlocked successfully."), "data":total_penalty}

    def get_task_hints(self, task):

        """ Method to get the task hints """

        hints = task._data.get("task_hints", {})
        return hints
