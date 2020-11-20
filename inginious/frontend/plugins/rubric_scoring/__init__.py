# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A demo plugin that adds a page """
import os

from inginious.frontend.plugins.utils import create_static_resource_page

from inginious.frontend.plugins.rubric_scoring.pages.api import pages
from inginious.frontend.plugins.rubric_scoring.pages.api import rubric_score_user_submissions
_STATIC_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, _, __, plugin_config):
    """ Init the plugin """
    plugin_manager.add_page(r'/rubric_scoring/static/(.*)', create_static_resource_page(_STATIC_FOLDER_PATH))


    use_minified = plugin_config.get("use_minified", True)

    if use_minified:
        plugin_manager.add_hook("css", lambda: "/rubric_scoring/static/css/rubric_scoring.min.css")
    else:
        plugin_manager.add_hook("css", lambda: "/rubric_scoring/static/css/rubric_scoring.css")




    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring', pages.CourseTaskListPage)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)', pages.TaskListSubmissionPage)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)/user/([a-z0-9A-Z\-_]+)',
                            rubric_score_user_submissions.UserSubmissionsPage)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
                            pages.SubmissionRubricPage)



    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring_temp', pages.CourseTaskListPageTemp)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring_temp/task/([a-z0-9A-Z\-_]+)',
                            pages.TaskListSubmissionPageTemp)
    plugin_manager.add_page(
        r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring_temp/task/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
        pages.SubmissionRubricPageTemp)



    plugin_manager.add_hook('course_admin_menu', pages.rubric_course_admin_menu_hook)

    renderer = plugin_manager._app.template_helper.get_custom_renderer('frontend/plugins/rubric_scoring/static', False)
    languages = plugin_manager._app.available_languages
    plugin_manager.add_hook("additional_body_html", lambda: str(renderer.register_students_modal(languages)))







