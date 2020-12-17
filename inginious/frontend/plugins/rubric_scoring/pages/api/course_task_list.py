# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Course task list for manual scoring page"""

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.rubric_scoring.pages.api import pages

base_renderer_path = pages.render_path

base_static_folder = pages.base_static_folder


class CourseTaskListPage(INGIniousAdminPage):
    """ List information about all tasks """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid)
        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, _ = self.get_course_and_check_rights(courseid)

        return self.page(course)

    def submission_url_generator(self, taskid):
        """ Generates a submission url """
        return "?format=taskid%2Fusername&tasks=" + taskid

    def page(self, course):
        """ Get all data and display the page """
        student_list = self.user_manager.get_course_registered_users(course, False)

        # Database query

        data = list(self.database.user_tasks.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "username": {"$in": student_list}
                        }
                },
                {
                    "$group":
                        {
                            "_id": "$taskid",
                            "viewed": {"$sum": 1},
                            "attempted": {"$sum": {"$cond": [{"$ne": ["$tried", 0]}, 1, 0]}},
                            "attempts": {"$sum": "$tried"},
                            "succeeded": {"$sum": {"$cond": ["$succeeded", 1, 0]}}

                        }
                }
            ]))
        # Number of students in the course
        num_students = len(student_list)
        # Load tasks and verify exceptions
        files = self.task_factory.get_readable_tasks(course)

        output = {}
        errors = []

        for task in files:
            try:
                output[task] = course.get_task(task)
            except Exception as inst:
                errors.append({"taskid": task, "error": str(inst)})
        tasks = OrderedDict(sorted(list(output.items()), key=lambda t: (t[1].get_order(), t[1].get_id())))

        # Now load additional information
        result = OrderedDict()
        for taskid in tasks:
            result[taskid] = {"name": tasks[taskid].get_name(self.user_manager.session_language()), "viewed": 0,
                              "attempted": 0, "attempts": 0, "succeeded": 0,
                              "url": self.submission_url_generator(taskid)}

        for entry in data:
            if entry["_id"] in result:
                result[entry["_id"]]["viewed"] = entry["viewed"]
                result[entry["_id"]]["attempted"] = entry["attempted"]
                result[entry["_id"]]["attempts"] = entry["attempts"]
                result[entry["_id"]]["succeeded"] = entry["succeeded"]

        return self.template_helper.get_custom_renderer(base_renderer_path) \
            .task_list(course, result, errors, num_students)
