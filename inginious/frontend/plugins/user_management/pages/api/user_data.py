import web
from collections import OrderedDict

from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.user_management.utils import get_collection_document
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


def _create_occurrences_dict(collection_names):
    collection_names = sorted(collection_names)
    return OrderedDict.fromkeys(collection_names, 0)


def _create_aggregation_to_count(username, information):
    query = [
        _create_match_aggregation(username, information),
        {
            "$count": "num_appearances"
        }
    ]
    return query


def _create_match_aggregation(username, information):
    key_name_in_json = "path"
    match_content = {}
    for info in information:
        # TODO: Be or, at the moment is and
        path = info[key_name_in_json]
        match_content[path] = username

    match = {
        "$match": match_content
    }
    return match


def has_username_key(collection_keys):
    return "username" in collection_keys


def get_count_username_occurrences(username, collection_manager):
    collection_name_list = collection_manager.get_collections_names()
    dictionary = _create_occurrences_dict(collection_name_list)
    collection_information = get_collection_document()

    def get_aggregation_result(name, query):
        ans = collection_manager.make_aggregation(name, query)
        return ans[0]["num_appearances"] if ans else 0

    for collection_name in collection_name_list:
        if collection_name in collection_information:
            collection_info = collection_information[collection_name]
            if collection_info[0]["path"] != "none":
                aggregation = _create_aggregation_to_count(username, collection_info)
                dictionary[collection_name] = get_aggregation_result(collection_name, aggregation)
        else:
            has_username = has_username_key(collection_manager.get_all_key_names(collection_name))
            if has_username:
                aggregation = _create_aggregation_to_count(username, [{"path": "username"}])
                dictionary[collection_name] = get_aggregation_result(collection_name, aggregation)

    return dictionary


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
