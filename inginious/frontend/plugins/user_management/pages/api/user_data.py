import web

from inginious.frontend.plugins.user_management.aggregation_generator import get_count_username_occurrences
from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class UserDataAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        username_or_email = get_mandatory_parameter(web.input(), "username_or_email")
        return self.get_user_data(username_or_email)

    def API_POST(self):
        pass

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
