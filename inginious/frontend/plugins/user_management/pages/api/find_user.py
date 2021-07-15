import pymongo.errors
import web
import re

from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


def _make_diacritic_insensitive(user_text):
    """ replaces each vowel with a set of the same vowel with basic diacritic symbols to be used in a regex """
    user_text = re.sub("a", "[a,á,à,ä,â,å,ã]", user_text, flags=re.IGNORECASE)
    user_text = re.sub("e", "[e,é,è,ë,ê]", user_text, flags=re.IGNORECASE)
    user_text = re.sub("i", "[i,í,ì,ï,î,ı]", user_text, flags=re.IGNORECASE)
    user_text = re.sub("o", "[o,ó,ò,ö,ô,õ]", user_text, flags=re.IGNORECASE)
    user_text = re.sub("u", "[u,ú,ù,ü]", user_text, flags=re.IGNORECASE)
    return user_text


def search_user(user_text, collections_manager, field=None):
    """ returns a list of users matching the search parameter.
    :param user_text: Is a mongodb regular expression
    :param collections_manager: Is the singleton class
    :param field: Is an optional parameter to indicate by which specific field to filter. By default, it filter for all
    field_names
     """

    def get_regex_pipeline(field_name):
        return {field_name: {"$regex": user_text, "$options": "i"}}

    search_fields = ["username", "email", "realname"]
    or_pipeline = []
    # It is not possible to use collation in mongodb regex. This is the alternative
    user_text = _make_diacritic_insensitive(user_text)

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
        try:
            list_of_users = search_user(user_string, collection_manager, field_search)
        except pymongo.errors.OperationFailure:
            return 500, {"error": _("Mongo operation fail")}
        return 200, {"users": list_of_users}
