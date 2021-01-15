# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" User list for a task in manual scoring page """

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.manual_scoring.pages.constants import get_render_path, get_use_minify

base_renderer_path = get_render_path()


def create_student_dict(user_list):
    """ Organize student's data in a dictionary """
    data = OrderedDict()
    for user in user_list:
        data[user["username"][0]] = {"username": user["username"][0],
                                     "realname": user["realname"][0], "grade": user["grade"]}
    return data


class StudentsListPage(INGIniousAdminPage):
    """ List users for a specific task """

    def GET_AUTH(self, course_id, task_id):
        """ Get request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
        return self.render_page(course, task_id, task)

    def render_page(self, course, task_id, task):
        """ Get all data and display the page """
        task_name = task.get_name(self.user_manager.session_language())
        user_list = self.get_students_list_and_max_score(course, task_id)
        url = 'manual_scoring'
        data = create_student_dict(user_list)

        self.add_css_file()

        return (
            self.template_helper.get_custom_renderer(base_renderer_path).students_list(course, data, task, task_name,
                                                                                       url)
        )

    def get_students_list_and_max_score(self, course, task_id):
        """ do request to db to get the data about users respect a task
            EXAMPLE:
                [{_id: Objectid(''), 'username':['student1'], 'realname':'pablo', 'taskid': 'pow', 'grade': 100.0},
                {...}, ...
                ]
        """
        user_list = list(self.database.submissions.aggregate(

            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "taskid": task_id,
                            "username": {"$in": self.user_manager.get_course_registered_users(course, False)},

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
                    "$project": {
                        "taskid": 1,
                        "username": 1,
                        "realname": "$user_info.realname",
                        "grade": {"$max": "$grade"}
                    }
                }

            ]))
        return user_list

    def add_css_file(self):
        """ add the css styles"""
        if get_use_minify():
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.min.css")
        else:
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.css")
