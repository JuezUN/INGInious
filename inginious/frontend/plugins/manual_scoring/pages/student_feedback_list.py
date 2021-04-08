# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
""" The list of feedbacks for a student """
from collections import defaultdict

from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.plugins.manual_scoring.constants import get_render_path, get_use_minify

base_renderer_path = get_render_path()


def get_task_titles(submissions):
    """ Get the title of the tasks. It is a dict between ids and names; if the name is empty, it takes the id"""
    titles = {}
    for task_id in submissions:
        submission_list = submissions[task_id]
        task_name = submission_list[0]["task_name"]
        if task_name != "":
            titles[task_id] = task_name
        else:
            titles[task_id] = task_id
    return titles


class StudentFeedbackListPage(INGIniousAuthPage):
    def GET_AUTH(self, course_id):
        """ Get request """
        course = self.course_factory.get_course(course_id)
        return self.render_page(course)

    def render_page(self, course):
        """ Get all data and display the page """
        db_data = self.get_submissions_with_feedback(course.get_id())
        data = self.create_feedback_dict(db_data, course)
        task_names = get_task_titles(data)
        self.add_css_file()
        return self.template_helper.get_custom_renderer(base_renderer_path).student_feedback_list(course, data,
                                                                                                  task_names)

    def get_submissions_with_feedback(self, course_id):
        """ does request to db to get the data about user's submissions
            EXAMPLE:
                [{_id: Objectid(''), 'submitted_on':datetime.datetime(), 'custom.custom_summary_result':'ACCEPTED',
                 'manual_scoring.grade': 100.0, 'manual_scoring.comment': "text", 'rubric_status': '["1-1","2-2"]',
                  'task_name': 'Multiplicación de dos números', 'task_id': 'Multiplicacion_dos_numeros'},
                {...}, ...
                ]
        """
        username = self.user_manager.session_username()
        data = list(self.database.submissions.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course_id,
                            "username": username,
                            "manual_scoring": {"$exists": "true"}
                        }
                },
                {
                    "$project": {
                        "submitted_on": 1,
                        "custom": 1,
                        "grade": 1,
                        "manual_scoring": 1,
                        "taskid": 1
                    }
                },
                {
                    "$sort":
                        {
                            "taskid": 1, "grade": -1, "submitted_on": -1
                        }
                }
            ]
        ))
        return data

    def add_css_file(self):
        """ add the css styles"""
        if get_use_minify():
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.min.css")
        else:
            self.template_helper.add_css("/manual_scoring/static/css/manual_scoring.css")

    def create_feedback_dict(self, feedback_list, course):
        """ Sort the information on a dictionary, classifying it by task id  """
        data = defaultdict(list)
        for feedback in feedback_list:
            submission = {
                "_id": feedback["_id"],
                "date": feedback["submitted_on"].strftime("%d/%m/%Y, %H:%M:%S"),
                "grade": feedback["grade"],
                "result": feedback["custom"]["custom_summary_result"],
                "manual_grade": feedback["manual_scoring"]["grade"],
                "task_name": course.get_task(feedback["taskid"]).get_name(self.user_manager.session_language()),
                "task_id": feedback["taskid"]
            }
            data[feedback["taskid"]].append(submission)
        return data
