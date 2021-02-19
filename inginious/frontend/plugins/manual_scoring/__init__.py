# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A manual scoring plugin for students submissions  """
import os

from inginious.frontend.plugins.utils import create_static_resource_page

from inginious.frontend.plugins.manual_scoring.pages import students_list, student_submissions, manual_scoring, \
    course_task_list, student_feedback_list, feedback
from .pages.constants import set_use_minified, get_manual_scoring_link_code, get_manual_scoring_feedback_hook

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, _, __, plugin_config):
    """ Init the plugin """
    plugin_manager.add_page(r'/manual_scoring/static/(.*)', create_static_resource_page(_static_folder_path))

    use_minified = plugin_config.get("use_minified", True)

    set_use_minified(use_minified)

    # Admin pages

    # First page of rubric scoring. It's a task list
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/manual_scoring',
                            course_task_list.CourseTaskListPage)
    # Second page of rubric scoring. It's a list of users who have done a submission
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/manual_scoring/task/([a-z0-9A-Z\-_]+)',
                            students_list.StudentsListPage)
    # Third page of rubric scoring. It's a list of submissions have done it by a student
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/manual_scoring/task/([a-z0-9A-Z\-_]+)/user/([a-z0-9A-Z\-_]+)',
                            student_submissions.StudentSubmissionsPage)
    # Fourth page. The rubric scoring page
    plugin_manager.add_page(
        r'/admin/([a-z0-9A-Z\-_]+)/manual_scoring/task/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
        manual_scoring.ManualScoringPage)

    plugin_manager.add_hook('course_admin_menu', get_manual_scoring_link_code)

    # Student pages
    plugin_manager.add_page(r'/feedback_list/([a-z0-9A-Z\-_]+)', student_feedback_list.StudentFeedbackListPage)
    plugin_manager.add_page(r'/submission_feedback/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
                            feedback.FeedbackPage)
    plugin_manager.add_hook('course_menu', get_manual_scoring_feedback_hook)
