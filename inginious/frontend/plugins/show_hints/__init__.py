import os
from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.hints_edit import edit_hints_tab, hints_modal, on_task_submit
from .pages.show_hints import show_hints
from .pages.api.hints_api import UserHintsAPI

_SHOW_HINT_STATIC_FILES = os.path.join(os.path.dirname(__file__), "static")

def init(plugin_manager, course_factory, client, config):

    plugin_manager.add_page(r'/show_hints/static/(.*)',
                            create_static_resource_page(_SHOW_HINT_STATIC_FILES))
    plugin_manager.add_page('/api/hints_api/', UserHintsAPI)

    plugin_manager.add_hook('task_editor_tab', edit_hints_tab)
    plugin_manager.add_hook('task_editor_footer', hints_modal)
    plugin_manager.add_hook('task_menu', show_hints)
    plugin_manager.add_hook('task_editor_submit', on_task_submit)
