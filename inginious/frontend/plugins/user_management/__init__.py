import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.api.find_user import FindUserAPI
from .pages.user_management import UserManagementPage
from .utils import set_use_minified, user_management_hook, on_user_sign_in
from .pages.api.user_data import UserDataAPI
from .pages.api.user_status import UserStatusAPI
from .collections_manager import CollectionsManagerSingleton

_BASE_STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')


def init(plugin_manager, course_factory, client, config):
    plugin_manager.add_page(r'/user_management/static/(.*)', create_static_resource_page(_BASE_STATIC_FOLDER))

    use_minified = config.get("use_minified", True)
    set_use_minified(use_minified)

    plugin_manager.add_page('/user_management', UserManagementPage)
    plugin_manager.add_page('/api/user_management', UserDataAPI)
    plugin_manager.add_page('/api/user_status', UserStatusAPI)
    plugin_manager.add_page('/api/find_user', FindUserAPI)

    plugin_manager.add_hook('open_session', on_user_sign_in)

    plugin_manager.add_hook("superadmin_options", lambda: user_management_hook(plugin_manager))
    CollectionsManagerSingleton(plugin_manager.get_database())
