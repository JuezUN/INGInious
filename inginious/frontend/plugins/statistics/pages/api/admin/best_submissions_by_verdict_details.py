import collections
import web

from .admin_api import AdminApi
from .utils import project_detail_best_user_tasks


class BestSubmissionsByVerdictStatisticsDetailApi(AdminApi):

    def _compute_details(self, course, task_id, summary_result):
        course_id = course.get_id()
        admins = list(set(course.get_staff() + self.user_manager._superadmins))

        user_tasks = self.database.user_tasks.aggregate([
            {
                "$match": {
                    "$and": [
                        {"courseid": course_id},
                        {"taskid": task_id},
                        {"username": {"$nin": admins}}
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "submissions",
                    "localField": "submissionid",
                    "foreignField": "_id",
                    "as": "submission"
                }
            },
            {
                "$unwind":
                    {
                        "path": "$submission",
                        "preserveNullAndEmptyArrays": True
                    }
            },
            {
                "$sort": collections.OrderedDict([
                    ("submission.submitted_on", -1),
                    ("username", 1)
                ])
            }
        ])
        return project_detail_best_user_tasks(user_tasks, summary_result)

    def API_GET(self):
        parameters = web.input()
        course_id = self.get_mandatory_parameter(parameters, 'course_id')
        course = self.get_course_and_check_rights(course_id)

        task_id = self.get_mandatory_parameter(parameters, 'task_id')
        summary_result = self.get_mandatory_parameter(parameters, 'summary_result')

        submissions = self._compute_details(course, task_id, summary_result)

        return 200, submissions
