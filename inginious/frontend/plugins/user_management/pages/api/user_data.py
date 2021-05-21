import web

from inginious.frontend.plugins.user_management.aggregation_generator import get_count_username_occurrences, \
    change_username, change_email, change_name
from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class UserDataAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        username_or_email = get_mandatory_parameter(web.input(), "username_or_email")
        return self.get_user_data(username_or_email)

    def API_POST(self):
        self.check_superadmin_rights()
        flag = False
        user_data = web.input()
        username = get_mandatory_parameter(user_data, "username")
        collections_manager = CollectionsManagerSingleton.get_instance()

        if "new_username" in web.input():
            flag = True
            change_username(username, user_data["new_username"], collections_manager)
        if "email" in web.input():
            flag = True
            change_email(username, user_data["email"], collections_manager)
        if "name" in web.input(username):
            flag = True
            change_name(username, user_data["name"], collections_manager)
        if not flag:
            return 400, {"message": _("no data to change")}

    def get_user_data(self, username_or_email):
        collections_manager = CollectionsManagerSingleton.get_instance()
        user_basic_data = self.get_basic_user_data(username_or_email)
        if user_basic_data:
            data = {"username": user_basic_data["username"],
                    "name": user_basic_data["realname"],
                    "email": user_basic_data["email"],
                    "count": get_count_username_occurrences(user_basic_data["username"], collections_manager)}
            return 200, data
        else:
            return 200, {"message": _("User no found")}

    def get_basic_user_data(self, username_or_email):
        data = self.database.users.find_one({'username': username_or_email})
        if data:
            return data
        return self.database.users.find_one({'email': username_or_email})
