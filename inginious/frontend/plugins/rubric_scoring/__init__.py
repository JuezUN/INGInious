# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A demo plugin that adds a page """
from inginious.frontend.plugins.rubric_scoring.pages.api import pages


def init(plugin_manager, _, _2, _3):
    """ Init the plugin """

    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring', pages.CourseTaskListPage)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)', pages.TaskListSubmissionPage)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring/task/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
                            pages.SubmissionRubricPage)



    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring_temp', pages.CourseTaskListPageTemp)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring_temp/task/([a-z0-9A-Z\-_]+)',
                            pages.TaskListSubmissionPageTemp)
    plugin_manager.add_page(
        r'/admin/([a-z0-9A-Z\-_]+)/rubric_scoring_temp/task/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
        pages.SubmissionRubricPageTemp)



    plugin_manager.add_hook('course_admin_menu', pages.rubric_course_admin_menu_hook)



