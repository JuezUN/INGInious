from inginious.frontend.parsable_text import ParsableText


class UserHintManager(object):
    """
        Manage the user's hints data in database. This includes the hints
        that were unlocked, the individual penalty, and cumulative
        penalty, to be applied in the student's final grade for the
        respective task.
    """

    def __init__(self, username, task_id, database):

        self._username = username
        self._task_id = task_id
        self._database = database

    def get_hint_content_by_status(self, hints):

        """
            This is a method to check each hint unlocked status, and return the left content
            if it is unlocked. Also set a 'True' value in the 'unlocked'
            attribute for the unlocked hints to show their additional data
            in the modal hints in the task.
        """
        user_hints = self.get_user_hints()

        if user_hints is None:
            self.insert_default_user_hints()
        else:
            self.update_unlocked_user_hints(user_hints, hints)

        user_hints = self.get_user_hints()
        unlocked_hints = user_hints["unlocked_hints"]

        hints_to_show = {}
        unlocked_hints_penalties = {}
        for hint in unlocked_hints:
            unlocked_hints_penalties[hint["id"]] = hint["penalty"]

        for key, hint in hints.items():
            unlocked_hints_data = {
                "title": hint["title"],
                "content": None,
                "penalty": hint["penalty"],
                "unlocked": False,
            }
            if hint["id"] in unlocked_hints_penalties.keys():
                parsed_hint_content = self.parse_rst_content(hint["content"])
                unlocked_hints_data["content"] = parsed_hint_content
                unlocked_hints_data["unlocked"] = True
                unlocked_hints_data["penalty"] = unlocked_hints_penalties[hint["id"]]

            hints_to_show[key] = unlocked_hints_data

        return hints_to_show

    def get_user_hints(self):
        return self._database.user_hints.find_one({"taskid": self._task_id,
                                                         "username": self._username})

    def update_unlocked_user_hints(self, user_hints, hints):

        """
            Method to delete hints that were removed from the task. These
            hints are removed in the unlocked user's hints.
        """
        unlocked_hints = user_hints["unlocked_hints"]
        hints_ids = [hint["id"] for hint in hints.values()]
        for hint in unlocked_hints:
            if not hint["id"] in hints_ids:
                self.remove_unlocked_hint(hint)

        self.update_total_penalty()

    def insert_default_user_hints(self):

        self._database.user_hints.insert(
            {"taskid": self._task_id, "username": self._username, "unlocked_hints": [], "penalty": 0})

    def is_hint_unlocked(self, hint_id):

        """ Method to check if the hint is already in the user hints """
        user_hints = self.get_user_hints()
        unlocked_hints = user_hints["unlocked_hints"]

        for hint in unlocked_hints:
            if hint_id == hint["id"]:
                return True

        return False

    def remove_unlocked_hint(self, hint_id):

        """ Method to delete a hint from the user unlocked hints"""
        self._database.user_hints.find_one_and_update(
            {"taskid": self._task_id, "username": self._username},
            {"$pull": {
                "unlocked_hints": hint_id
            }
            })

    def unlock_hint(self, hint_id, task_hints):

        """ Method to add the new unlocked hint in the user unlocked hints """
        if not self.is_hint_unlocked(hint_id):
            self._database.user_hints.find_one_and_update({"taskid": self._task_id, "username": self._username},
                                                          {"$push": {
                                                              "unlocked_hints": {
                                                                  "penalty": task_hints[hint_id]["penalty"],
                                                                  "id": task_hints[hint_id]["id"]
                                                              }
                                                          }
                                                          })
            self.update_total_penalty()

        return 200, ""

    def update_total_penalty(self):

        """ Method needed to compare the saved hints per student, and the task hints
            to change penalty to the student
        """
        new_penalty = 0;
        user_hints = self.get_user_hints()
        unlocked_hints = user_hints["unlocked_hints"]

        for hint in unlocked_hints:
            new_penalty += float(hint["penalty"])

        new_penalty = min(new_penalty, 100.0)

        self._database.user_hints.update({"taskid": self._task_id, "username": self._username},
                                         {"$set": {"penalty": new_penalty}
                                          })

    def parse_rst_content(self, content):

        if content is None:
            return content
        parse_content = ParsableText(content, "rst").parse()
        return parse_content
