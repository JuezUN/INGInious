import web
import json
import inginious.frontend.pages.api._api_page as api

from inginious.frontend.plugins.user_management.aggregation_generator import get_count_username_occurrences
from inginious.frontend.plugins.user_management.find_generator import get_submissions_running, \
    get_custom_test_running, get_num_open_user_sessions
from inginious.frontend.plugins.user_management.update_generator import change_username, change_email, change_name, \
    make_user_changes_register, close_user_sessions, add_block_user, remove_block_user
from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


def any_process_running(username, collection_manager):
    submissions = get_submissions_running(username, collection_manager)
    custom_test = get_custom_test_running(username, collection_manager)
    return True if submissions or custom_test else False


def block_user(username, collection_manager):
    if any_process_running(username, collection_manager):
        raise api.APIError(409, _("There are user's process running"))
    if get_num_open_user_sessions(username, collection_manager):
        close_user_sessions(username, collection_manager)
    add_block_user(username, collection_manager)


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
        try:
            block_user(username, collections_manager)
        except api.APIError as error:
            return error.status_code, {"error": error.return_value}
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
            return 400, {"error": _("no data to change")}

        new_username = user_data["new_username"] if username_count > 0 else username
        _, user_final_info = self.get_user_data(new_username)
        make_user_changes_register(user_original_info, user_final_info, collections_manager)

        remove_block_user(new_username, collections_manager)

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

    def inform_user_changes(self, user_original_info, user_final_info):
        pass
