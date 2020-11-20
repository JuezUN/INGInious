import web
import os
from inginious.frontend.plugins.rubric_scoring.pages.api.rubric_wdo import RubricWdo
from bson.objectid import ObjectId
from pymongo import MongoClient
import gridfs

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from collections import OrderedDict

_BASE_RENDERER_PATH = 'frontend/plugins/rubric_scoring/pages/templates'

_BASE_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../static')


class UserSubmissionsPage(INGIniousAdminPage):
    """ List user's submissions respect a task """
    def GET_AUTH(self, course_id, task_id, username):
        """ GET request """
        course, task = self.get_course_and_check_rights(course_id, task_id)
       # user = self.user_manager.course_is_user_registered(course_id, username)


        return self.page(course, task_id, task, username, )

    def page(self, course, task_id, task, username):
        """ get submissions for user and display page """

        url = 'rubric_scoring'

        result = list(self.database.submissions.aggregate(
            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "taskid": task_id,
                            "username": username

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
                        "result": 1,
                        "submitted_on": 1,
                        "username": 1,
                        "custom": 1,
                        "grade": 1,
                        "realname": 1
                    }
                },
                {
                    "$sort":
                        {
                             "grade": -1, "submitted_on": -1
                        }
                }

            ]))

        data = OrderedDict()
        task_name = course.get_task(task_id).get_name(self.user_manager.session_language())

        for entry in result:
            data[entry["_id"]] = {"taskid": entry["taskid"], "result": entry["result"], "_id": entry["_id"],
                                  "username": entry["username"], "date": entry["submitted_on"], "grade": entry["grade"],
                                  "summary_result": entry["custom"]["custom_summary_result"], "realname": entry["realname"]
                                  }

            if "rubric_score" not in entry["custom"]:
                data[entry["_id"]]["rubric_score"] = "not grade"
            else:
                data[entry["_id"]]["rubric_score"] = entry["custom"]["rubric_score"]

        return (
            self.template_helper.get_custom_renderer(_BASE_RENDERER_PATH).user_submissions(
                course, data, task, task_name, username, url)
            )
