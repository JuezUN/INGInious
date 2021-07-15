import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.code_preview import code_preview_tab
from .pages.code_preview import on_task_editor_submit
from .pages.api.task_code_preview_api import TaskCodePreviewAPI
from .constants import set_use_minified, add_static_files_on_task_page

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, _1, _2, config):
    plugin_manager.add_page("/api/code_preview/", TaskCodePreviewAPI)
    plugin_manager.add_page(r"/code_preview/static/(.*)", create_static_resource_page(_static_folder_path))

    set_use_minified(config.get("use_minified", True))

    plugin_manager.add_hook("add_task_page_static_files", add_static_files_on_task_page)

    plugin_manager.add_hook("task_editor_tab", code_preview_tab)
    plugin_manager.add_hook("task_editor_submit", on_task_editor_submit)
