from inginious.frontend.plugins.utils.superadmin_utils import SuperadminAuthPage
from ..utils import get_use_minified, BASE_TEMPLATE_FOLDER


class UserManagementPage(SuperadminAuthPage):
    """ User management page """
    def GET_AUTH(self, *args, **kwargs):
        """ get request """
        self.check_superadmin_rights()

        self.add_css_and_js_files()
        return self.template_helper.get_custom_renderer(BASE_TEMPLATE_FOLDER).user_management()

    def add_css_and_js_files(self):
        """ add the ccs and js files """
        self.template_helper.add_javascript("/static/js/message_box.js")
        if get_use_minified():
            self.template_helper.add_css("/user_management/static/css/user_management.min.css")
            self.template_helper.add_javascript("/user_management/static/js/user_management.min.js")
        else:
            self.template_helper.add_css("/user_management/static/css/user_management.css")
            self.template_helper.add_javascript("/user_management/static/js/user_management.js")
            self.template_helper.add_javascript("/user_management/static/js/user_data.js")
            self.template_helper.add_javascript("/user_management/static/js/confirmation_modal.js")
            self.template_helper.add_javascript("/user_management/static/js/user_status.js")
            self.template_helper.add_javascript("/user_management/static/js/user_list.js")
