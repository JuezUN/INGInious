# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" User list for a task in manual scoring page """

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.manual_scoring.pages import constants

base_renderer_path = constants.render_path


def create_student_dict(user_list):
    """ Organize student's data in a dictionary """
    data = OrderedDict()
    for user in user_list:
        data[user["username"][0]] = {"username": user["username"][0],
                                     "realname": user["realname"], "grade": user["grade"]}
    return data


class StudentsListPage(INGIniousAdminPage):
    """ List users for a specific task """

    def GET_AUTH(self, course_id, task_id):
        """ Get request """
        course, task = self.get_course_and_check_rights(course_id, task_id)

        return self.render_page(course, task_id, task)

    def render_page(self, course, task_id, task):
        """ Get all data and display the page """
        task_name = course.get_task(task_id).get_name(self.user_manager.session_language())
        user_list = self.get_students_list_and_max_score(course, task_id)
        url = 'manual_scoring'
        data = create_student_dict(user_list)

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
                    "$replaceRoot": {"newRoot": {"$mergeObjects": [{"$arrayElemAt": ["$user_info", 0]}, "$$ROOT"]}}
                },

                {
                    "$project": {
                        "taskid": 1,
                        "username": 1,
                        "realname": 1,
                        "grade": {"$max": "$grade"}
                    }
                },

            ]))
        return user_list
