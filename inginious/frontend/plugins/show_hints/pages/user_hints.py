
from inginious.frontend.parsable_text import ParsableText

class UserHint(object):

    """ Manage the user hints information """

    def __init__(self, username, task_id, database):

        self._username = username
        self._task_id = task_id
        self._database = database

    def check_locked_hint_status(self, hints):

        """ Method to check each hint status, and return the content
            if it is allowed
        """
        user_hints = self._database.user_hints.find_one({"taskid":  self._task_id,
                                            "username":  self._username})
        if user_hints is None:
            user_hints = self.create_hint_list_for_user()
            return 200, ""

        self.update_allowed_hints_list(user_hints, hints)

        to_show_hints = {}
        allowed_hints = user_hints["allowedHints"]
        for key in hints:
            to_show_hint_content = {
                "title": hints[key]["title"],
                "content": None,
                "penalty": hints[key]["penalty"],
                "allowed_to_see": False,
            }
            if hints[key]["id"] in [hint["id"] for i, hint in enumerate(allowed_hints)]:

                parse_content = self.parse_rst_content(hints[key]["content"])
                to_show_hint_content["content"] = parse_content
                to_show_hint_content["allowed_to_see"] = True
                to_show_hint_content["penalty"] = [hint["penalty"] for i, hint in enumerate(allowed_hints) if hint["id"] == hints[key]["id"]]

            to_show_hints[key] = to_show_hint_content

        return to_show_hints

    def update_allowed_hints_list(self, user_hints, hints):

        """ Method to compare the user hints with the task hints, and update them"""
        allowedHints = user_hints["allowedHints"]
        hints_id = {key:hint["id"] for key, hint in hints.items()}
        for hint in allowedHints:
            if not hint["id"] in hints_id.values():
                self.delete_hint_from_allowed(hint)
                a = 1

        self.update_total_penalty()

    def create_hint_list_for_user(self):

        user_hints = self._database.user_hints.insert({"taskid": self._task_id, "username": self._username, "allowedHints": [], "penalty": 0})
        return user_hints

    def check_allowed_hint_in_database(self, hint_id):

        """ Method to check if the hint is already in the user hints """
        user_hints = self._database.user_hints.find_one({"taskid": self._task_id, "username": self._username})
        allowed_hints = user_hints["allowedHints"]

        if hint_id in [allowed_hints[i]["id"] for i, value in enumerate(allowed_hints)]:
            return True

        return False

    def delete_hint_from_allowed(self, hint_id):

        """ Method to delete a hint from the user allowed hints"""
        self._database.user_hints.find_one_and_update(
            {"taskid": self._task_id, "username": self._username},
            {"$pull": {
                "allowedHints": hint_id
            }
        })

    def add_hint_on_allowed(self, hint_id, task_hints):

        """ Method to add the new unlocked hint in the user allowed hints """
        if not self.check_allowed_hint_in_database(hint_id):

            self._database.user_hints.find_one_and_update({"taskid": self._task_id, "username": self._username},
                                                                { "$push": {
                                                                    "allowedHints": {
                                                                        "penalty": task_hints[hint_id]["penalty"],
                                                                        "id": task_hints[hint_id]["id"]
                                                                        }
                                                                    }
                                                                })
            total_penalty = self.update_total_penalty()

        return 200, ""

    def update_total_penalty(self):

        """ Method needed to compare the saved hints per student, and the task hints
            to change penalty to the student
        """
        new_penalty = 0;
        user_hints = self._database.user_hints.find_one({"taskid": self._task_id, "username": self._username})
        allowed_hints = user_hints["allowedHints"]

        for hint in allowed_hints:
           new_penalty += float(hint["penalty"])

        if new_penalty > 100:
            new_penalty = 100

        self._database.user_hints.update({"taskid": self._task_id, "username": self._username},
                                         {"$set" : {"penalty": new_penalty}
                                        })

        return new_penalty

    def parse_rst_content(self, content):

        if content is None:
            return content
        parse_content = ParsableText(content,"rst").parse()
        return parse_content

