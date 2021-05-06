import collections
import web

from .admin_api import AdminApi
from .utils import task_submissions_detail


class SubmissionsByVerdictDetailsApi(AdminApi):

    def _compute_details(self, course, task_id, summary_result, later_submissions=False):
        course_id = course.get_id()
        admins = list(set(course.get_staff() + self.user_manager._superadmins))

        later_submissions_filter = True
        if not later_submissions:
            later_submissions_filter = {"$in": [False, None]}

        submissions = self.database.submissions.aggregate([
            {"$match":
                {
                    "courseid": course_id,
                    "custom.custom_summary_result": summary_result,
                    "taskid": task_id,
                    "username": {"$nin": admins},
                    "is_later_submission": later_submissions_filter
                }
            },
            {"$unwind":
                {
                    "path": "$username",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$sort": collections.OrderedDict([
                    ("submitted_on", -1),
                    ("username", 1)
                ])
            }
        ])

        return task_submissions_detail(submissions)

    def API_GET(self):
        parameters = web.input()
        course_id = self.get_mandatory_parameter(parameters, 'course_id')
        course = self.get_course_and_check_rights(course_id)

        task_id = self.get_mandatory_parameter(parameters, 'task_id')
        summary_result = self.get_mandatory_parameter(parameters, 'summary_result')
        later_submissions = self.get_mandatory_parameter(parameters, "later_submissions")

        submissions = self._compute_details(course, task_id, summary_result, later_submissions == "true")

        return 200, submissions
