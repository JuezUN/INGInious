import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.task_editorial import editorial_task_tab, EditorialCourseAdminPage, editorial_course_admin_menu


def init(plugin_manager, course_factory, client , config):

    use_minified = config.get("use_minified", True)

    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/editorial', EditorialCourseAdminPage)

    plugin_manager.add_hook('task_editor_tab',editorial_task_tab)

    plugin_manager.add_hook('course_admin_menu',editorial_course_admin_menu)


