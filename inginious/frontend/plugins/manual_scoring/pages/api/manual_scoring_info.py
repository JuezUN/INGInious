# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
""" It contents the API who returns manual scoring data """
from inginious.frontend.plugins.manual_scoring.constants import get_dict_value
from inginious.frontend.plugins.utils.admin_api import AdminApi


class ManualScoringInfoApi(AdminApi):
    """ API to get the manual scoring data resume """

    def API_GET(self, course_id):
        """ GET request """
        course = self.get_course_and_check_rights(course_id)
        data = self.create_manual_scoring_dict(course)
        return 200, data

    def get_manual_scoring_results(self, course):
        """ it does a request to db to get the data about all course's manual scoring
            EXAMPLE:
                [{_id: Objectid(''), 'username':['user'], 'realname':['pepe'],
                 'taskid': 'pow', 'submitted_on': datetime.datetime(),
                 'custom_summary_result': '["1-1","2-2"]', 'grade': '100.0',
                 manual_scoring: {'comment': 'text', 'grade': '4.6', 'rubric_status': '["0-2","1-4", "2-4"]'} },
                {...}, ...
                ] """
        course_id = course.get_id()
        student_list = self.user_manager.get_course_registered_users(course, False)
        data = list(self.database.submissions.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course_id,
                            "username": {"$in": student_list},
                            "manual_scoring": {"$exists": "true"}
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
                        "grade": 1,
                        "manual_scoring": 1,
                        "submitted_on": 1,
                        "custom_summary_result": "$custom.custom_summary_result"
                    }
                }

            ]
        ))
        return data

    def create_manual_scoring_dict(self, course):
        """ returns an array of dictionaries with the students information """
        manual_scoring_data = self.get_manual_scoring_results(course)
        data = []
        for submission in manual_scoring_data:
            submission_info = {
                "_id": str(submission["_id"]),
                "username": submission["username"][0],
                "real_name": submission["realname"][0],
                "task_id": submission["taskid"],
                "task_name": course.get_task(submission["taskid"]).get_name(self.user_manager.session_language()),
                "result": get_dict_value(submission, "custom_summary_result"),
                "grade": submission["grade"],
                "manual_grade": submission["manual_scoring"]["grade"],
                "date": submission["submitted_on"].strftime("%d/%m/%Y, %H:%M:%S")
            }
            data.append(submission_info)
        return data
