
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
        data = self._database.user_hints.find_one({"taskid":  self._task_id,
                                            "username":  self._username})
        if data is None:
            data = self.create_hint_list_for_user()
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

    def create_hint_list_for_user(self):

        data = self._database.user_hints.insert({"taskid": self._task_id, "username": self._username, "allowedHints": [], "penalty": 0})
        return data

    def check_allowed_hint_in_database(self, hint_id):

        """ Method to check if the hint is already in the user hints """
        data = self._database.user_hints.find_one({"taskid": self._task_id, "username": self._username})
        allowed_hints = data["allowedHints"]

        if hint_id in allowed_hints:
            return True

        return False

    def add_hint_on_allowed(self, hint_id, task_hints):

        """ Method to add the new unlocked hint in the user allowed hints """
        if not self.check_allowed_hint_in_database(hint_id):

            data = self._database.user_hints.find_one_and_update({"taskid": self._task_id, "username": self._username},{
                                                                "$push": {
                                                                    "allowedHints":hint_id
                                                                }
                                                            })
            self.update_total_penalty(data, task_hints)

            return 200, ""

    def get_total_penalty(self):

        data = self._database.user_hints.find_one({"taskid": self._task_id, "username": self._username});
        penalty = data["penalty"]

        return penalty

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

        self._database.user_hints.update({"taskid": data["taskid"], "username": data["username"]},
                                         {"$set" : {"penalty": new_penalty}
                                        })

    def parse_rst_content(self, content):

        if content is None:
            return content
        parse_content = ParsableText(content,"rst").parse()
        return parse_content

