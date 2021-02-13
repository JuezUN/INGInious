# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A student's Submissions list page"""

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.manual_scoring.pages.constants import get_use_minify, get_render_path

base_renderer_path = get_render_path()


def create_submissions_dict(submissions_list):
    """ Organize all data in a dictionary """
    data = OrderedDict()
    default_grade = "No grade"
    for submission in submissions_list:
        data[submission["_id"]] = {
            "_id": submission["_id"],
            "date": submission["submitted_on"],
            "grade": submission["grade"],
            "summary_result": submission["custom"]["custom_summary_result"],
        }
        if "manual_scoring" in submission:
            data[submission["_id"]]["manual_grade"] = submission["manual_scoring"]["grade"]
        else:
            data[submission["_id"]]["manual_grade"] = default_grade
    return data


class StudentSubmissionsPage(INGIniousAdminPage):
    """ List user's submissions respect a task """

    def GET_AUTH(self, course_id, task_id, username):
        """ GET request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
        self.add_css_file()
        return self.render_page(course, task_id, task, username, )

    def render_page(self, course, task_id, task, username):
        """ get submissions for a user and display page """
        url = 'manual_scoring'
        task_name = course.get_task(task_id).get_name(self.user_manager.session_language())
        name = self.user_manager.get_user_realname(username)
        result = self.get_student_submissions(course.get_id(), task_id, username)
        data = create_submissions_dict(result)
        return (
            self.template_helper.get_custom_renderer(base_renderer_path).student_submissions(
                course, data, task, task_name, username, name, url)
        )

    def get_student_submissions(self, course_id, task_id, username):
        """ do request to db to get the data about user's submissions
            EXAMPLE:
                [{_id: Objectid(''), 'submitted_od':datetime.datetime(), 'custom.custom_summary_result':'ACCEPTED',
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
                    "$lookup":
                        {
                            "from": "users",
                            "localField": "username",
                            "foreignField": "username",
                            "as": "user_info"
                        }
                },
                {
                    "$replaceRoot": {"newRoot": {"$mergeObjects": [{"$arrayElemAt": ["$user_info", 0]}, "$$ROOT"]}}
                },

                {
                    "$project": {
                        "submitted_on": 1,
                        "custom": 1,
                        "grade": 1,
                        "manual_scoring": 1
                    }
                },
                {
                    "$sort":
                        {
                            "grade": -1, "submitted_on": -1
                        }
                }

            ]))
        return data

    def add_css_file(self):
        if get_use_minify():
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.min.css")
        else:
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.css")
