import os

_BASE_RENDERER_PATH = os.path.dirname(__file__)
BASE_TEMPLATE_FOLDER = os.path.join(_BASE_RENDERER_PATH, "pages/templates")
_use_minified = True


def set_use_minified(value):
    global _use_minified
    _use_minified = value


def get_use_minified():
    return _use_minified


def user_management_hook(plugin_manager):
    if plugin_manager.get_user_manager().user_is_superadmin():
        return _(""""<li><a href='/user_management' class='navbar-link'>
        <i class="fa fa-user-plus" aria-hidden="true"></i> User Management</a></li>""")
