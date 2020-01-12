import os
import web
import json
import datetime

from inginious.frontend.plugins.utils import create_static_resource_page, get_mandatory_parameter
from inginious.frontend.plugins.analytics.manager import AnalyticsManager
from inginious.client.client_sync import ClientSync
from inginious.frontend.pages.api._api_page import APIAuthenticatedPage
from inginious.frontend.parsable_text import ParsableText
from bson.objectid import ObjectId

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")

def customInputManagerWithCurriedClient(client):
    class CustomInputManager(APIAuthenticatedPage):
        def __init__(self):
            self._client = client
            self.analytics_manager = AnalyticsManager(self.database)

        def add_unsaved_job(self, task, inputdata):
            temp_client = ClientSync(self._client)
            return temp_client.new_job(task, inputdata)

        def API_GET(self):
            request_params = web.input()
            submission_id = get_mandatory_parameter(request_params, "submission")

            # A mongo request for the submission and his input
            # How do i do this?
            things = self.database.submissions.aggregate([
                {
                    '$match' : {
                        "_id" : ObjectId(submission_id)
                    }
                },
                {
                    "$project" : {
                        "_id": 0,
                        "taskid": 1,
                        "courseid": 1
                    }
                }
            ])
            return 200, list(things)[0]

        def API_POST(self):
            request_params = web.input()
            analytics_params = {
                'username': self.user_manager.session_username(),
                'service': 'custom_input',
                'date' : datetime.datetime.now(),
                'session_id' : self.user_manager.session_id()
            }
            self.analytics_manager.add_visit(**analytics_params)

            courseid = get_mandatory_parameter(request_params, "courseid")
            course = self.course_factory.get_course(courseid)
            taskid = get_mandatory_parameter(request_params, "taskid")
            task = self.task_factory.get_task(course, taskid)

            try:
                init_var = {
                    problem.get_id(): problem.input_type()()
                    for problem in task.get_problems() if problem.input_type() in [dict, list]
                }
                userinput = task.adapt_input_for_backend(web.input(**init_var))
                for k in userinput:
                    userinput[k] = userinput[k].replace("\r", "")
                result, grade, problems, tests, custom, archive, stdout, stderr = self.add_unsaved_job(task, userinput)

                data = {
                    "status": ("done" if result[0] == "success" or result[0] == "failed" else "error"),
                    "result": result[0],
                    "text": ParsableText(result[1]).parse(),
                    "stdout": custom.get("custom_stdout", ""),
                    "stderr": custom.get("custom_stderr", "")
                }
                web.header('Content-Type', 'application/json')
                return 200, json.dumps(data)

            except Exception as ex:
                web.header('Content-Type', 'application/json')
                return 200, json.dumps({"status": "error", "text": str(ex)})

    return CustomInputManager

def init(plugin_manager, course_factory, client, plugin_config):
    plugin_manager.add_page(r'/custom_input/static/(.*)', create_static_resource_page(_static_folder_path))
    plugin_manager.add_page("/api/custom_input/", customInputManagerWithCurriedClient(client))

    use_minified = plugin_config.get("use_minified", True)
    if use_minified:
        plugin_manager.add_hook("javascript_footer", lambda: "/custom_input/static/custom_input.min.js")
    else:
        plugin_manager.add_hook("javascript_footer", lambda: "/custom_input/static/custom_input.js")
