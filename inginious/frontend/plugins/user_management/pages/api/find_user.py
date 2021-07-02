import web

from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


def search_user(user_text, collections_manager, field=None):
    """ returns a list of users matching the search parameter.
    :param user_text: Is a mongodb regular expresion
    :param collections_manager: Is the singleton class
    :param field: Is an optional parameter to indicate by which specific field to filter. By default, it filter for all
    field_names
     """

    def get_regex_pipeline(field_name):
        return {field_name: {"$regex": user_text, "$options": "i"}}

    search_fields = ["username", "email", "realname"]
    or_pipeline = []

    if field in search_fields:
        or_pipeline.append(get_regex_pipeline(field))
    else:
        or_pipeline = [get_regex_pipeline(field_name) for field_name in search_fields]

    user_filter = {
        "$match": {
            "$or": or_pipeline
        }}
    projection = {"$project": {"_id": 0, "username": 1, "realname": 1, "email": 1
                               }
                  }
    query = [user_filter, projection]

    return list(collections_manager.make_aggregation("users", query))


class FindUserAPI(SuperadminAPI):
    """ An API to find users whom are related to the search parameter """

    def API_GET(self):
        """ Get request. returns a list of users matching the search parameter """
        self.check_superadmin_rights()
        user_string = get_mandatory_parameter(web.input(), "user")
        field_search = web.input().get("field", None)
        collection_manager = CollectionsManagerSingleton.get_instance()
        return 200, {"users": search_user(user_string, collection_manager, field_search)}
