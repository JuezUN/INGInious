# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A manual scoring plugin for students submissions  """

from inginious.frontend.plugins.utils import create_static_resource_page

from .pages import students_list, student_submissions, manual_scoring, course_task_list, student_feedback_list, feedback
from .constants import set_use_minified, get_manual_scoring_link_code, get_feedback_link_code, get_static_folder_path
from .pages.api.rst_parser import RstParserAPI
from .pages.api.manual_scoring_info import ManualScoringInfoApi
from .pages.api.upload_custom_rubric import UploadCustomRubric


def init(plugin_manager, _, __, plugin_config):
    """ Init the plugin """
    plugin_manager.add_page(r'/manual_scoring/static/(.*)', create_static_resource_page(get_static_folder_path()))

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

    plugin_manager.add_page("/api/manual_scoring/upload_custom_rubric", UploadCustomRubric)

    plugin_manager.add_hook('course_admin_menu', get_manual_scoring_link_code)

    # Student pages

    plugin_manager.add_page(r'/feedback_list/([a-z0-9A-Z\-_]+)', student_feedback_list.StudentFeedbackListPage)
    plugin_manager.add_page(r'/submission_feedback/([a-z0-9A-Z\-_]+)/submission/([a-z0-9A-Z\-_]+)',
                            feedback.FeedbackPage)
    plugin_manager.add_page(r'/api/parse_rst', RstParserAPI)
    plugin_manager.add_page(r'/api/manual_scoring/([a-z0-9A-Z\-_]+)', ManualScoringInfoApi)
    plugin_manager.add_hook('course_menu', get_feedback_link_code)
