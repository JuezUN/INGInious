# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Course task list for manual scoring page"""
import json

from collections import OrderedDict
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from ..constants import get_use_minify, get_render_path
from .rubric import get_rubric_content

base_renderer_path = get_render_path()


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
        total_students = len(self.user_manager.get_course_registered_users(course, False))
        tasks_data = self.get_tasks_data(course)

        self.add_css_and_js_file()

        rubric_content = get_rubric_content(self.user_manager, course.get_fs())

        upload_custom_rubric_template = \
            self.template_helper.get_custom_renderer(base_renderer_path, False).custom_rubric_modal(rubric_content,
                                                                                                    json.dumps(
                                                                                                        rubric_content))

        page_template = self.template_helper.get_custom_renderer(base_renderer_path).course_task_list(course,
                                                                                                      tasks_data,
                                                                                                      total_students)

        return str(page_template) + str(upload_custom_rubric_template)

    def get_tasks_data(self, course):
        """ cross the task data and return the result """
        attempted_succeeded_per_task = self.get_total_attempted_and_succeeded_per_task(course)
        task_dict = self.get_ordered_course_tasks(course)
        for task in attempted_succeeded_per_task:
            task_id = task["_id"]
            if task_id in task_dict:
                task_dict[task_id]["attempted"] = task["attempted"]
                task_dict[task_id]["succeeded"] = task["succeeded"]

        # Remove tasks that have no attempts
        task_dict = OrderedDict({key: val for key, val in task_dict.items() if val["attempted"] > 0})
        task_dict = OrderedDict(sorted(task_dict.items(), key=lambda x: x[1]["name"]))
        return task_dict

    def get_total_attempted_and_succeeded_per_task(self, course):
        """ do request to db to get the number of attempted and succeeded per task
            EXAMPLE:
                [{_id:'sum_two_numbers', 'attempted':2, 'succeeded':2},
                {...}, ...
                ]
        """
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

    def get_ordered_course_tasks(self, course):
        """ get all the tasks in a course.
        it is necessary because no name is found on db """
        tasks = self.task_factory.get_all_tasks(course)
        task_dict = OrderedDict()
        for task_id, task in tasks.items():
            task_dict[task_id] = {"name": task.get_name_or_id(self.user_manager.session_language()),
                                  "attempted": 0, "succeeded": 0}
        return task_dict

    def add_css_and_js_file(self):
        """ add the css styles and js files"""
        self.template_helper.add_javascript(
            "https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        if get_use_minify():
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.min.css")
            self.template_helper.add_javascript("/manual_scoring/static/js/course_task_list.min.js")
        else:
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.css")
            self.template_helper.add_javascript("/manual_scoring/static/js/message_box.js")
            self.template_helper.add_javascript("/manual_scoring/static/js/task_list_main.js")
