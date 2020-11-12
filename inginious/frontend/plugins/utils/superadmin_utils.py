import web
from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.pages.api._api_page import APIAuthenticatedPage, APIForbidden


class SuperadminAPI(APIAuthenticatedPage):
    def check_superadmin_rights(self):
        if not self.user_manager.user_is_superadmin():
            raise APIForbidden()


class SuperadminAuthPage(INGIniousAuthPage):
    def check_superadmin_rights(self):
        if not self.user_manager.user_is_superadmin():
            raise web.notfound()
