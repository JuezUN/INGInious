import web

from inginious.frontend.plugins.user_management.aggregation_generator import search_user
from inginious.frontend.plugins.user_management.collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class FindUserAPI(SuperadminAPI):
    """ An API to find users whom are related with the search parameter """
    def API_GET(self):
        """ Get request. returns a list of users matching the search parameter """
        self.check_superadmin_rights()
        user_string = get_mandatory_parameter(web.input(), "user")
        field = web.input()["field"] if "field" in web.input() else None
        collection_manager = CollectionsManagerSingleton.get_instance()
        return 200, {"users": search_user(user_string, collection_manager, field)}