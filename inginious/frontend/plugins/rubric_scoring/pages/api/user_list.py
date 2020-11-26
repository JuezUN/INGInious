from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from collections import OrderedDict

from inginious.frontend.plugins.rubric_scoring.pages.api import pages

base_renderer_path = pages.RENDERER_PATH

base_static_folder = pages.BASE_STATIC_FOLDER


class UserListPage(INGIniousAdminPage):
    def GET_AUTH(self, course_id, task_id):
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/PapaParse/4.3.6/papaparse.min.js")
        self.template_helper.add_javascript("https://cdn.plot.ly/plotly-1.30.0.min.js")
        self.template_helper.add_javascript("https://cdn.jsdelivr.net/npm/lodash@4.17.4/lodash.min.js")

        return self.page(course, task_id, task)

    def page(self, course, task_id, task):
        """ Get all data and display the page """

        url = 'rubric_scoring'

        result = list(self.database.submissions.aggregate(

            [
                {
                    "$match":
                        {
                            "courseid": course.get_id(),
                            "taskid": task_id,
                            "username": {"$in": self.user_manager.get_course_registered_users(course, False)},

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
                        "realname": 1
                    }
                },

            ]))

        # get task name
        task_name = course.get_task(task_id).get_name(self.user_manager.session_language())

        data = OrderedDict()
        for entry in result:
            data[entry["username"][0]] = {"username": entry["username"][0], "realname": entry["realname"]}

        return (
            self.template_helper.get_custom_renderer(base_renderer_path).user_list(
                course, data, task, task_name, url)
        )
