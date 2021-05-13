# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A student's Submissions list page"""

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.manual_scoring.constants import get_use_minify, get_render_path, get_dict_value

base_renderer_path = get_render_path()


def create_submissions_dict(submissions_list):
    """ Organize all data in a dictionary """
    data = OrderedDict()
    default_grade = _("No grade")
    for submission in submissions_list:
        data[submission["_id"]] = {
            "_id": submission["_id"],
            "date": submission["submitted_on"].strftime("%d/%m/%Y, %H:%M:%S"),
            "grade": get_dict_value(submission, "grade"),
            "result": get_dict_value(submission, "custom", "custom_summary_result"),
            "is_later_submission": submission.get("is_later_submission", False),
        }
        if "manual_scoring" in submission:
            data[submission["_id"]]["manual_grade"] = submission["manual_scoring"]["grade"]
        else:
            data[submission["_id"]]["manual_grade"] = default_grade
    data = OrderedDict(sorted(data.items(), key=lambda x: x[1]["grade"], reverse=True))
    return data


class StudentSubmissionsPage(INGIniousAdminPage):
    """ List user's submissions respect a task """

    def GET_AUTH(self, course_id, task_id, username):
        """ GET request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
        return self.render_page(course, task_id, task, username, )

    def render_page(self, course, task_id, task, username):
        """ get submissions for a user and display page """
        url = 'manual_scoring'
        task_name = course.get_task(task_id).get_name_or_id(self.user_manager.session_language())
        name = self.user_manager.get_user_realname(username)
        result = self.get_student_submissions(course.get_id(), task_id, username)
        data = create_submissions_dict(result)

        self.add_css_file()

        return (
            self.template_helper.get_custom_renderer(base_renderer_path).student_submissions(
                course, data, task, task_name, username, name, url)
        )

    def get_student_submissions(self, course_id, task_id, username):
        """ does request to db to get the data about user's submissions
            EXAMPLE:
                [{_id: Objectid(''), 'submitted_on':datetime.datetime(), 'custom.custom_summary_result':'ACCEPTED',
                 'manual_scoring.grade': 100.0, 'manual_scoring.comment': "text", 'rubric_status': '["1-1","2-2"]' },
                {...}, ...
                ]
        """
        data = list(self.database.submissions.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course_id,
                            "taskid": task_id,
                            "username": username
                        }
                },
                {
                    "$project": {
                        "submitted_on": 1,
                        "custom": 1,
                        "grade": 1,
                        "manual_scoring": 1,
                        "is_later_submission": 1
                    }
                },
                {
                    "$sort":
                        {
                            "submitted_on": -1
                        }
                }

            ]))
        return data

    def add_css_file(self):
        """ add the css styles"""
        if get_use_minify():
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.min.css")
        else:
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.css")
