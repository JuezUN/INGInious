import os
from collections import OrderedDict
from .collections_manager import CollectionsManagerSingleton
from inginious.frontend.plugins.utils import read_json_file

_BASE_RENDERER_PATH = os.path.dirname(__file__)
BASE_TEMPLATE_FOLDER = os.path.join(_BASE_RENDERER_PATH, "pages/templates")
_static_folder_path = os.path.join(os.path.dirname(__file__), "static")
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


def get_collection_document():
    file_path = os.path.join(_static_folder_path, 'json/collections_info.json')
    return OrderedDict(sorted(read_json_file(file_path).items()))


def on_user_sign_in(username):
    collections_manager = CollectionsManagerSingleton.get_instance()
    user = list(collections_manager.make_find_request("users", {"username": username}, {"block": 1}))
    if user:
        return user[0]["block"] if "block" in user[0] else False
    return True
