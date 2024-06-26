import os
from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.hints_edit import edit_hints_tab, get_hints_edit_modal_template, on_task_submit
from .pages.show_hints import show_hints, get_user_total_penalty
from .pages.api.user_hints_api import UserHintsAPI
from .pages.api.edit_hints_api import EditHintsAPI
from .pages.api.hints_mode_api import HintsModeAPI
from .pages.user_hint_manager import UserHintManagerSingleton
from .pages.constants import set_use_minified

_SHOW_HINT_STATIC_FILES = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, course_factory, client, config):
    set_use_minified(config.get("use_minified", True))
    plugin_manager.add_page(r'/task_hints/static/(.*)',
                            create_static_resource_page(_SHOW_HINT_STATIC_FILES))
    plugin_manager.add_page('/api/user_hints_api/', UserHintsAPI)
    plugin_manager.add_page('/api/edit_hints_api/', EditHintsAPI)
    plugin_manager.add_page('/api/hints_mode_api/', HintsModeAPI)

    plugin_manager.add_hook('task_editor_tab', edit_hints_tab)
    plugin_manager.add_hook('task_editor_footer', get_hints_edit_modal_template)
    plugin_manager.add_hook('task_menu', show_hints)
    plugin_manager.add_hook('task_editor_submit', on_task_submit)

    UserHintManagerSingleton(plugin_manager.get_database())
    plugin_manager.add_hook('show_hints', get_user_total_penalty)
