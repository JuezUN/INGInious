from inginious.frontend.parsable_text import ParsableText


class UserHintManagerSingleton(object):
    """
        Manage the user's hints data in database. This includes the hints
        that were unlocked, the individual penalty, and cumulative
        penalty, to be applied in the student's final grade for the
        respective task.
    """

    _instance = None

    @staticmethod
    def get_instance(database=None):

        if not UserHintManagerSingleton._instance:
            UserHintManagerSingleton(database)
        return UserHintManagerSingleton._instance

    def __init__(self, database):

        if UserHintManagerSingleton._instance:
            raise Exception("")
        else:
            self._database = database
            UserHintManagerSingleton._instance = self

    def get_hint_content_by_status(self, task, username, hints):
        """
            This is a method to check each hint unlocked status, and return the left content
            if it is unlocked. Also set a 'True' value in the 'unlocked'
            attribute for the unlocked hints to show their additional data
            in the modal hints in the task.
        """
        task_id = task.get_id()

        if(task.is_group_task()):
            users_group = self._database.aggregations.find_one(
                {"courseid": task.get_course_id(), "groups.students": username},
                {"groups": {"$elemMatch": {"students": username}}}
            )
            if users_group:
                students = users_group["groups"][0]['students']
        else:
            students = [username]

        user_hints = self.get_user_hints(task_id, students)
        
        unlocked_hints_penalties = {}
        data = {}

        if user_hints:
            unlocked_hints = user_hints["unlocked_hints"]
            data["total_penalty"] = user_hints["total_penalty"]
            for hint in unlocked_hints:
                unlocked_hints_penalties[hint["id"]] = hint["penalty"]

        hints_to_show = {}
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

        data["hint_to_show"] = hints_to_show

        return data

    def get_task_users_hints(self, task_id):
        return self._database.user_hints.find({"taskid": task_id})

    def get_user_hints(self, task_id, username):
        return self._database.user_hints.find_one({"taskid": task_id,
                                                   "username": username})

    def update_unlocked_users_hints(self, task_id, task_hints):
        """
            Method to check and delete hints that were removed from the task. These
            hints are removed from unlocked hints for all users in task.
        """
        task_hints_ids = [hint["id"] for hint in task_hints.values()]

        # Find the documents that need to be updated
        task_users_hints = list(self._database.user_hints.find(
            {"taskid": task_id,
             "unlocked_hints": {
                 "$elemMatch": {
                     "id": {
                         "$nin": task_hints_ids
                     }
                 }
             }}))

        for user_hints in task_users_hints:
            username = user_hints["username"]
            self.remove_deleted_hints(task_id, username, task_hints_ids)

    def insert_default_user_hints(self, task_id, username, shared_hints=False):

        self._database.user_hints.insert(
            {"taskid": task_id, "username": username, "unlocked_hints": [], "total_penalty": 0, "shared_hints": shared_hints})

    def is_hint_unlocked(self, task_id, username, hint_id):
        """ Method to check if the hint is already in the user hints """
        user_hints = self.get_user_hints(task_id, username)
        unlocked_hints = user_hints["unlocked_hints"]

        for hint in unlocked_hints:
            if hint_id == hint["id"]:
                return True

        return False

    def remove_deleted_hints(self, task_id, username, hints_ids):
        """ Method to delete hints from the user unlocked hints"""
        self._database.user_hints.find_one_and_update(
            {"taskid": task_id, "username": username},
            {"$pull": {
                "unlocked_hints": {
                    "id": {
                        "$nin": hints_ids
                    }
                }
            }
            }
        )
        self.update_total_penalty(task_id, username)


    def unlock_hint(self, task, username, hint_id, task_hints):

        task_id = task.get_id()

        # Check if task is a group task

        if(task.is_group_task()):
            users_group = self._database.aggregations.find_one(
                {"courseid": task.get_course_id(), "groups.students": username},
                {"groups": {"$elemMatch": {"students": username}}}
            )
            if users_group:
                username = users_group["groups"][0]['students']
        else:
            username = [username]

        # Check if user hints document already exists in database
        user_hints = self.get_user_hints(task_id, username)

        # Create the user hints document if doesn't exists
        if user_hints is None:
            self.insert_default_user_hints(task_id, username, task.is_group_task())

        """ Method to add the new unlocked hint in the user unlocked hints """
        if not self.is_hint_unlocked(task_id, username, task_hints[hint_id]["id"]):

            self._database.user_hints.find_one_and_update({"taskid": task_id, "username": username},
                                                          {"$push": {
                                                              "unlocked_hints": {
                                                                  "penalty": task_hints[hint_id]["penalty"],
                                                                  "id": task_hints[hint_id]["id"]
                                                              }
                                                          }
            })
            self.update_total_penalty(task_id, username)

        return 200, ""

    def update_total_penalty(self, task_id, username):
        """ Method needed to compare the saved hints per student, and the task hints
            to change penalty to the student
        """
        new_penalty = 0
        user_hints = self.get_user_hints(task_id, username)
        unlocked_hints = user_hints["unlocked_hints"]

        for hint in unlocked_hints:
            new_penalty += float(hint["penalty"])

        new_penalty = min(new_penalty, 100.0)

        self._database.user_hints.find_one_and_update({"taskid": task_id, "username": username},
                                                      {"$set": {"total_penalty": new_penalty}
                                                       })

    def on_change_task_submission_mode(self, task_id, task_group):

        if(task_group):  
            self._database.user_hints.delete_many({"taskid":task_id,"groups":not task_group})
        else:
            self._database.user_hints.delete_many({"taskid":task_id,"groups":not task_group})
        
        return task_id                                               

    def parse_rst_content(self, content):

        if content is None:
            return content
        parse_content = ParsableText(content, "rst").parse()
        return parse_content
