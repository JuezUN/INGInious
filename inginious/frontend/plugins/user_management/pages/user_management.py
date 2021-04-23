from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAuthPage
from ..utils import get_use_minified, BASE_TEMPLATE_FOLDER


class UserManagementPage(SuperadminAuthPage):
    def GET_AUTH(self, *args, **kwargs):
        self.check_superadmin_rights()
        return self.template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER).user_management()

    def get_minify_files(self):
        pass
