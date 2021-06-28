import web
import json
import inginious.frontend.pages.api._api_page as api

from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.user_management.update_user_data import close_user_sessions, add_block_user, \
    change_email, change_name, change_username, make_user_changes_register, remove_block_user
from inginious.frontend.plugins.user_management.user_information import get_count_username_occurrences
from inginious.frontend.plugins.user_management.user_status import get_submissions_running, get_custom_test_running, \
    get_num_open_user_sessions
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


def any_process_running(username, collection_manager):
    """ indicates whether the user is running any process """
    submissions = get_submissions_running(username, collection_manager)
    custom_test = get_custom_test_running(username, collection_manager)
    return True if submissions or custom_test else False


def block_user(username, collection_manager):
    """ block a user to prevent new process while the data is changing """
    if any_process_running(username, collection_manager):
        raise api.APIError(409, _("There are user's process running"))
    if get_num_open_user_sessions(username, collection_manager):
        close_user_sessions(username, collection_manager)
    add_block_user(username, collection_manager)


def inform_user_changes(user_original_info, user_final_info, collection_manager):
    """ Send an email to the student that their user data has been modified """

    def get_changes():
        text = ""
        key_dict = {"username": _("Username"), "email": _("Email"), "name": _("Name")}
        keys = list(user_original_info.keys())
        keys.remove("count")
        for key in keys:
            if user_original_info[key] != user_final_info[key]:
                text += """    - """ + key_dict[key] + ": " + user_original_info[key] + " -> " + user_final_info[
                    key] + "\n"
        return text
    user_email = user_final_info["email"]
    subject = _("Changes in your user account")
    hash_link = get_user_activation_link(user_final_info["username"], collection_manager)
    post_data_auth_prob = _("- If at some point you had authentication problems, it may be due to the change process.")
    post_data_contact_admin = _("- If you think any change is wrong, please contact the administrator.")
    post_data_hash = _(
        """- We have noticed that you have not yet activated your account, please click on the following link:
        """) + hash_link
    final_post = post_data_hash if hash_link else post_data_auth_prob
    message = _("""Some changes have been made to your account:
""") + get_changes() + _(""" To keep in mind:
    """) + post_data_contact_admin + """ 
    """ + final_post
    try:
        web.sendmail(web.config.smtp_sendername, user_email, subject, message)
    except (ValueError, TypeError):
        raise api.APIError(500, _("Something went  wrong when we sent the information email to the user"))


def get_user_activation_link(username, collection_manager):
    """ Returns the activation link if the user has not activated the account """
    user = collection_manager.make_find_one_request("users", {"username": username})
    if "activate" in user:
        return web.ctx.home + "/register?activate=" + user["activate"]
    return ""


class UserDataAPI(SuperadminAPI):
    """ API to get information about a user """

    def API_GET(self):
        """ Get request. Returns data about a user """
        self.check_superadmin_rights()
        username = get_mandatory_parameter(web.input(), "username")
        user_data = self.get_user_data(username)
        return 200, user_data

    def API_POST(self):
        """ request to change one or more of the basic data of a user: username, realname or email """
        self.check_superadmin_rights()
        flag = False
        user_data = web.input()
        username = get_mandatory_parameter(user_data, "username")
        collections_manager = CollectionsManagerSingleton.get_instance()
        user_original_info = self.get_user_data(username)

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
        user_final_info = self.get_user_data(new_username)
        make_user_changes_register(user_original_info, user_final_info, collections_manager)

        remove_block_user(new_username, collections_manager)

        try:
            inform_user_changes(user_original_info, user_final_info, collections_manager)
        except api.APIError as error:
            return error.status_code, {"username": username_count, "email": email_count, "name": name_count,
                                       "error": error.return_value}

        return 200, {"username": username_count, "email": email_count, "name": name_count}

    def get_user_data(self, username):
        """ Returns data of a user """
        collections_manager = CollectionsManagerSingleton.get_instance()
        user_basic_data = self.database.users.find_one({'username': username})
        if user_basic_data:
            collection_data, unknown_collections = get_count_username_occurrences(user_basic_data["username"],
                                                                                  collections_manager)
            data = {"username": user_basic_data["username"],
                    "name": user_basic_data["realname"],
                    "email": user_basic_data["email"],
                    "count": collection_data,
                    "unknown_collections": unknown_collections}
            return data
        else:
            return {"user": _("User no found")}
