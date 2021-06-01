import web
import json
from inginious.frontend.plugins.user_management.aggregation_generator import get_count_username_occurrences
from inginious.frontend.plugins.user_management.update_generator import change_username, change_email, change_name, \
    make_user_changes_register
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
        ans, user_original_info = self.get_user_data(username)

        username_count = 0
        email_count = 0
        name_count = 0

        self.block_user(username)
        if "email" in user_data:
            flag = True
            email_count = change_email(username, user_data["email"], collections_manager)
        if "name" in user_data:
            flag = True
            name_count = change_name(username, user_data["name"], collections_manager)
        if "new_username" in user_data:
            flag = True
            collection_name_list = json.loads(get_mandatory_parameter(user_data, "collection_list"))
            username_count = change_username(username, user_data["new_username"], collections_manager,
                                             collection_name_list)
        if not flag:
            return 400, {"message": _("no data to change")}

        new_username = user_data["new_username"] if username_count > 0 else username
        _, user_final_info = self.get_user_data(new_username)
        make_user_changes_register(user_original_info, user_final_info, collections_manager)
        self.unlock_user(new_username)
        self.inform_user_changes(user_original_info, user_final_info)

        return 200, {"username": username_count, "email": email_count, "name": name_count}

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

    def block_user(self, username):
        pass

    def unlock_user(self, new_username):
        pass

    def inform_user_changes(self, user_original_info, user_final_info):
        pass
