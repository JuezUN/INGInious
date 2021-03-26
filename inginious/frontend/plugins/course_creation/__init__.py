# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .constants import add_course_creation_main_menu
from .api.create_course_api import CreateCourseAPI

_STATIC_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, course_factory, _1, plugin_config):
    """
        Init the plugin.
        Available configuration in configuration.yaml:
        ::

            - plugin_module: "inginious.frontend.plugins.course_creation"
            - use_minified: true or false. True by default.
    """

    use_minified = plugin_config.get("use_minified", True)

    plugin_manager.add_page(r"/course_creation/static/(.*)", create_static_resource_page(_STATIC_FOLDER_PATH))

    plugin_manager.add_page(r"/api/create_course", CreateCourseAPI)

    plugin_manager.add_hook("main_menu", add_course_creation_main_menu(plugin_manager, course_factory, use_minified))
