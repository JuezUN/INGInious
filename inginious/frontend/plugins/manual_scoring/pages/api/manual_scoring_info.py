from collections import defaultdict

from inginious.frontend.plugins.utils.admin_api import AdminApi


class ManualScoringInfoApi(AdminApi):
    def API_GET(self, course_id):
        course = self.get_course_and_check_rights(course_id)
        data = self.create_manual_scoring_dict(course)
        return 200, data

    def get_manual_scoring_results(self, course):
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
                    "$replaceRoot": {"newRoot": {"$mergeObjects": [{"$arrayElemAt": ["$user_info", 0]}, "$$ROOT"]}}
                },
                {
                    "$project": {
                        "taskid": 1,
                        "username": 1,
                        "realname": 1,
                        "grade": 1,
                        "manual_scoring": 1,
                        "submitted_on": 1,
                        "custom.custom_summary_result": 1
                    }
                }

            ]
        ))
        return data

    def create_manual_scoring_dict(self, course):
        manual_scoring_data = self.get_manual_scoring_results(course)
        data = []

        for submission in manual_scoring_data:
            submission_info = {
                "_id": str(submission["_id"]),
                "username": submission["username"][0],
                "real_name": submission["realname"],
                "task_id": submission["taskid"],
                "task_name": course.get_task(submission["taskid"]).get_name(self.user_manager.session_language()),
                "grade": submission["grade"],
                "manual_grade": submission["manual_scoring"]["grade"],
                "date": submission["submitted_on"].strftime("%d/%m/%Y, %H:%M:%S"),
                "result": submission["custom"]["custom_summary_result"]
            }
            data.append(submission_info)
        return data
