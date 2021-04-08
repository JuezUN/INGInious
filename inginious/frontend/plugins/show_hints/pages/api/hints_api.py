import os
import web

from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIError
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.common.course_factory import InvalidNameException, CourseNotFoundException
from inginious.frontend.parsable_text import ParsableText

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

        return 200, self.check_locked_hint_status(self.get_task_hints(task), task_id, username)

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

        self.add_hint_on_allowed(hint_id, task_id, username, task_hints)

        return 200, {"status":"success","message":"Unlocked list updated successfully (Penalty was applied)"}

    def get_task_hints(self, task):

        """ Method to get the task hints """
        hints = task._data.get("task_hints", [])
        return hints

    def check_locked_hint_status(self, hints, task_id, username):

        """ Method to check each hint status, and return the content
            if it is allowed
        """
        data = self.database.user_hints.find_one({"taskid": task_id,
                                            "username": username})
        if data is None:
            data = self.create_hint_list_for_user(task_id, username)
            return 200, ""

        to_show_hints = []
        allowedHints = data["allowedHints"]
        for key in hints:
            to_show_hint_content = {
                "title": hints[key]["title"],
                "content": None,
                "penalty": hints[key]["penalty"],
                "allowed_to_see": False,
            }
            if key in allowedHints:

                parse_content = self.parse_rst_content(hints[key]["content"])
                to_show_hint_content["content"] = parse_content
                to_show_hint_content["allowed_to_see"] = True

            to_show_hints.append(to_show_hint_content)

        return to_show_hints

    def create_hint_list_for_user(self, task_id, username):

        data = self.database.user_hints.insert({"taskid": task_id, "username": username, "allowedHints": [], "penalty": 0})
        return data

    def check_allowed_hint_in_database(self, hint_id, task_id, username):

        """ Method needed to check if the hint is already in the user hints """
        data = self.database.user_hints.find_one({"taskid": task_id, "username": username})
        allowed_hints = data["allowedHints"]

        if hint_id in allowed_hints:
            return True

        return False

    def add_hint_on_allowed(self, hint_id, task_id, username, task_hints):

        """ Method to add the new unlocked hint in the user allowed hints """
        if not self.check_allowed_hint_in_database(hint_id, task_id, username):

            data = self.database.user_hints.find_one_and_update({"taskid": task_id, "username": username},{
                                                                "$push": {
                                                                    "allowedHints":hint_id
                                                                }
                                                            })
            self.update_total_penalty(data, task_hints)

            return 200, ""

    def update_total_penalty(self, data, task_hints):

        """ Method needed to compare the saved hints per student, and the task hints
            to change penalty to the student
        """
        new_penalty = 0;
        allowed_hints = data["allowedHints"]

        for key, hint in task_hints.items():
            if key in allowed_hints:
                new_penalty += float(hint["penalty"])

        if new_penalty > 100:

            new_penalty = 100

        self.database.user_hints.update({"taskid": data["taskid"], "username": data["username"]},
                                         {"$set" :
                                              {"penalty": new_penalty}
                                        })


    def parse_rst_content(self, content):

        if content is None:
            return content
        parse_content = ParsableText(content,"rst").parse()
        return parse_content
