import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.task_tutorial import tutorial_tab


def init(plugin_manager, course_factory, client , config):

    use_minified = config.get("use_minified", True)

    plugin_manager.add_hook('task_editor_tab',tutorial_tab)


