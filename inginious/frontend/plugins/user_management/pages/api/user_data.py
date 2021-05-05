import web

from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAPI


class UserDataAPI(SuperadminAPI):
    def API_GET(self):
        self.check_superadmin_rights()
        username = get_mandatory_parameter(web.input(), "username")


    def API_POST(self):
        pass
