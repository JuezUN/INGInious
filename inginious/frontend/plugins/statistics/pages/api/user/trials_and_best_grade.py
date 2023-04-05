import web

from .user_api import UserApi
import inginious.frontend.pages.api._api_page as api
from inginious.common.course_factory import CourseNotFoundException, CourseUnreadableException, InvalidNameException
from inginious.common.exceptions import TaskNotFoundException


class TrialsAndBestGradeApi(UserApi):
    def statistics(self):
        username = self.user_manager.session_username()
        course_id = web.input().course_id

        best_submissions = self.database.user_tasks.aggregate([
            {
                "$match":
                    {
                        "username": username,
                        "courseid": course_id
                    }
            },
            {
                "$lookup":
                    {
                        "from": "submissions",
                        "localField": "submissionid",
                        "foreignField": "_id",
                        "as": "submission"
                    }
            },
            {
                "$unwind":
                    {
                        "path": "$submission"
                    }
            },
            {
                "$sort":
                    {
                        "submission.submitted_on": 1
                    }

            },
            {
                "$project":
                    {
                        "_id": 0,
                        "result": {
                            "$ifNull": [
                                "$submission.custom.custom_summary_result",
                                {"$cond": [
                                    {"$eq": ["$submission.result", "success"]},
                                    "ACCEPTED",
                                    "WRONG_ANSWER"
                                ]}
                            ]
                        },
                        "taskid": 1,
                        "tried": 1,
                        "grade": 1
                    }
            }
        ])

        # Add the tasks names
        best_submissions_with_name = []
        for sub in list(best_submissions):
            try:
                course = self.course_factory.get_course(course_id)
            except (CourseNotFoundException, InvalidNameException, CourseUnreadableException):
                raise api.APIError(400, {"error": "The course does not exist or the user does not have permissions"})

            try:
                task = course.get_task(sub['taskid'])
            except TaskNotFoundException:
                continue

            sub['task_name'] = task.get_name_or_id(self.user_manager.session_language())
            best_submissions_with_name.append(sub)

        return 200, list(best_submissions_with_name)
