from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAuthPage
from ..utils import get_use_minified, BASE_TEMPLATE_FOLDER


class UserManagementPage(SuperadminAuthPage):
    def GET_AUTH(self, *args, **kwargs):
        self.check_superadmin_rights()

        self.add_css_and_js_files()
        return self.template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER).user_management()

    def add_css_and_js_files(self):
        if get_use_minified():
            pass
        else:
            self.template_helper.add_css("/user_management/static/css/user_management.css")
            self.template_helper.add_javascript("/user_management/static/js/user_management.js")
