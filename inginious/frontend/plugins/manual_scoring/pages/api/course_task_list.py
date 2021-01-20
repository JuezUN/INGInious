# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Course task list for manual scoring page"""

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.manual_scoring.pages.api import pages

base_renderer_path = pages.render_path

base_static_folder = pages.base_static_folder


class CourseTaskListPage(INGIniousAdminPage):
    """ List information about all tasks """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid)
        return self.render_page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, _ = self.get_course_and_check_rights(courseid)

        return self.render_page(course)

    def render_page(self, course):
        """ Get all data and display the page """
        num_students = len(self.user_manager.get_course_registered_users(course, False))
        data = self.get_task_information(course)

        return self.template_helper.get_custom_renderer(base_renderer_path) \
            .task_list(course, data, num_students)

    def get_task_information(self, course):
        """ cross the task data and return the result """
        attempted_succeeded_per_task = self.get_tasks_and_its_num_of_attempted_and_succeeded(course)
        tasks = self.get_task_in_order_dict(course)
        task_dict = OrderedDict()

        for task in attempted_succeeded_per_task:
            task_id = task["_id"]
            task_dict[task_id] = {"name": tasks[task_id].get_name(self.user_manager.session_language()),
                                  "attempted": task["attempted"], "succeeded": task["succeeded"]}

        return task_dict

    def get_tasks_and_its_num_of_attempted_and_succeeded(self, course):
        """ do request to db to get the number of attempted and succeeded per task """
        course_id = course.get_id()
        student_list = self.user_manager.get_course_registered_users(course, False)
        data = list(self.database.user_tasks.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course_id,
                            "username": {"$in": student_list}
                        }
                },
                {
                    "$group":
                        {
                            "_id": "$taskid",
                            "attempted": {"$sum": {"$cond": [{"$ne": ["$tried", 0]}, 1, 0]}},
                            "succeeded": {"$sum": {"$cond": ["$succeeded", 1, 0]}}

                        }
                }
            ]))

        return data

    def get_task_in_order_dict(self, course):
        """ get all the tasks in a course.
        it is necessary because no name is found on db """
        task_array = self.task_factory.get_all_tasks(course)
        return OrderedDict(sorted(list(task_array.items()), key=lambda t: (t[1].get_order(), t[1].get_id())))
