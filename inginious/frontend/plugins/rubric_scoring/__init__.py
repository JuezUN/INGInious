# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A manual scoring plugin for students submissions  """
import os

from inginious.frontend.plugins.utils import create_static_resource_page

from inginious.frontend.plugins.rubric_scoring.pages.api import pages
from inginious.frontend.plugins.rubric_scoring.pages.api import user_submissions
from inginious.frontend.plugins.rubric_scoring.pages.api import course_task_list
from inginious.frontend.plugins.rubric_scoring.pages.api import user_list
from inginious.frontend.plugins.rubric_scoring.pages.api import rubric_scoring

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, _, __, plugin_config):
    """ Init the plugin """
    plugin_manager.add_page(r'/rubric_scoring/static/(.*)', create_static_resource_page(_static_folder_path))
    # Minified
    use_minified = plugin_config.get("use_minified", True)

    if use_minified:
        plugin_manager.add_hook("css", lambda: "/rubric_scoring/static/css/rubric_scoring.min.css")
        plugin_manager.add_hook("javascript_footer", lambda: "/rubric_scoring/static/js/rubric_scoring.min.js")
    else:
        plugin_manager.add_hook("css", lambda: "/rubric_scoring/static/css/rubric_scoring.css")
        plugin_manager.add_hook("javascript_footer", lambda: "/rubric_scoring/static/js/rubric_scoring_init.js")

    # Add pages
    # First page of rubric scoring. It's a task list
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring',
                            course_task_list.CourseTaskListPage)
    # Second page of rubric scoring. It's a list of users who have done a submission
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)',
                            user_list.UserListPage)
    # Third page of rubric scoring. It's a list of submissions have done it by a student
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)/user/([a-z0-9A-Z\-_]+)',
                            user_submissions.UserSubmissionsPage)
    # Fourth page. The rubric scoring page
    plugin_manager.add_page(
        r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
        rubric_scoring.RubricScoringPage)

    plugin_manager.add_hook('course_admin_menu', pages.rubric_course_admin_menu_hook)
