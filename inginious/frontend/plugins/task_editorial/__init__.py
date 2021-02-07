import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.task_editorial import editorial_task_tab, editorial_task_preview, check_editorial_submit
from .pages.api.solution_notebook_api import SolutionNotebookApi

_TASK_EDITORIAL_STATIC_FOLDER_PATH_ = os.path.join(os.path.dirname(__file__), "static")

def init(plugin_manager, course_factory, client , config):

    use_minified = config.get("use_minified", True)

    plugin_manager.add_page(r"/task_editorial/static/(.*)",create_static_resource_page(_TASK_EDITORIAL_STATIC_FOLDER_PATH_))
    plugin_manager.add_page("/api/task_editorial/", SolutionNotebookApi)

    if (use_minified):
        plugin_manager.add_hook("javascript_footer", lambda: "/task_editorial/static/task_editorial.min.js")
    else:
        plugin_manager.add_hook("javascript_footer", lambda: "/task_editorial/static/task_editorial.js")
        plugin_manager.add_hook("javascript_footer", lambda: "/task_editorial/static/task_editorial_preview.js")

    plugin_manager.add_hook('task_editor_tab',editorial_task_tab)
    plugin_manager.add_hook('task_menu',editorial_task_preview)
    plugin_manager.add_hook('task_editor_submit', check_editorial_submit)
