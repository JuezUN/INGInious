import inginious.frontend.pages.api._api_page as api


class SuperadminAPI(api.APIAuthenticatedPage):
    def check_superadmin_rights(self):
        if not self.user_manager.user_is_superadmin():
            raise api.APIForbidden()
