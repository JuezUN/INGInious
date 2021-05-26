import os
import web

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException
from ..user_hint_manager import UserHintManagerSingleton


class UserHintsAPI(APIAuthenticatedPage):

    @property
    def user_hint_manager(self) -> UserHintManagerSingleton:
        """ Returns user hint manager singleton """
        return UserHintManagerSingleton.get_instance()

    def API_GET(self):

        """
            For all the hints that the user has unlocked, get the left necessary content by
            each hint to show them in task view (Content in RST format, applied penalty, and
            unlocked hint status).
        """

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        username = self.user_manager.session_username()

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": _("The course does not exist or the user does not have access.")})

        try:
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": _("The task does not exist in the course.")})

        if not self.user_manager.course_is_user_registered(course, username):
            raise APIError(400, {"error": _("The user is not registered in this course.")})

        hints_data = {}

        try:
            hints_data = self.user_hint_manager.get_hint_content_by_status(task_id,username,self.get_task_hints(task))
        except Exception:
            raise APIError(400, {"message": _("An error occurred while getting the user's hints.")})

        return 200, {"status": "success", "data": hints_data}

    def API_POST(self):

        """
            Set a unlocked user's hint in the database as 'unlocked', and
            set it's own penalty and total penalty
        """

        input_data = web.input()
        course_id = get_mandatory_parameter(input_data, 'course_id')
        task_id = get_mandatory_parameter(input_data, 'task_id')
        username = self.user_manager.session_username()
        hint_id = get_mandatory_parameter(input_data, 'hint_id')

        try:
            course = self.course_factory.get_course(course_id)
        except (InvalidNameException, CourseNotFoundException):
            raise APIError(400, {"error": _("The course does not exist or the user does not have access.")})

        try:
            task = self.task_factory.get_task(course, task_id)
        except Exception:
            raise APIError(400, {"error": _("The task does not exist in the course.")})

        if not self.user_manager.course_is_user_registered(course, username):
            raise APIError(400, {"error": _("The user is not registered in this course.")})

        task_hints = self.get_task_hints(task)

        try:
            self.user_hint_manager.unlock_hint(task_id, username, hint_id, task_hints)
        except Exception:
            return 200, {"status": "error", "message": _(
                "An error occurred while updating status of the hint. The hint does not exist in the database.")}

        return 200, {"status": "success", "message": _("Hint unlocked successfully.")}

    def get_task_hints(self, task):

        """ Method to get the task hints """

        hints = task._data.get("task_hints", {})
        return hints
