import json
import web

from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.client.client_sync import ClientSync
from inginious.frontend.pages.api._api_page import APIAuthenticatedPage
from inginious.frontend.parsable_text import ParsableText


def custom_input_manager_multilang(client):
    """
    This function returns a CustomInputManager in charge of running the student's code against a custom input
    given by the student. This is only for multilang tasks.
    :param client:
    :return: CustomInputManager
    """

    class CustomInputManager(APIAuthenticatedPage):
        def __init__(self):
            self._client = client

        def add_unsaved_job(self, task, inputdata):
            temp_client = ClientSync(self._client)
            return temp_client.new_job(task, inputdata, "Custom input - " + self.user_manager.session_username())

        def API_POST(self):
            request_params = web.input()

            courseid = get_mandatory_parameter(request_params, "courseid")
            course = self.course_factory.get_course(courseid)
            taskid = get_mandatory_parameter(request_params, "taskid")
            task = self.task_factory.get_task(course, taskid)

            try:
                init_var = {
                    problem.get_id(): problem.input_type()()
                    for problem in task.get_problems() if problem.input_type() in [dict, list]
                }
                user_input = task.adapt_input_for_backend(web.input(**init_var))
                for key, value in user_input.items():
                    if type(value) is str:
                        user_input[key] = user_input[key].replace("\r", "")
                result, grade, problems, tests, custom, archive, stdout, stderr = self.add_unsaved_job(task, user_input)

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
