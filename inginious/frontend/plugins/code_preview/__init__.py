import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.code_preview import code_preview_tab
from .pages.code_preview import on_task_editor_submit
from .pages.api.task_preview_file_api import TaskPreviewFileAPI

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, course_factory, client, config):
    plugin_manager.add_page("/api/code_preview/", TaskPreviewFileAPI)
    plugin_manager.add_page(r"/code_preview/static/(.*)", create_static_resource_page(_static_folder_path))

    use_minified = config.get("use_minified", True)

    if use_minified:
        plugin_manager.add_hook("javascript_footer", lambda: "/code_preview/static/js/code_preview_load.min.js")
    else:
        plugin_manager.add_hook("javascript_footer", lambda: "/code_preview/static/js/code_preview_load.js")

    plugin_manager.add_hook("task_editor_tab", code_preview_tab)
    plugin_manager.add_hook("task_editor_submit", on_task_editor_submit)
