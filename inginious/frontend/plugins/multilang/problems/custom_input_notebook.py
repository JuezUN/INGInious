import json
import web

from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.client.client_sync import ClientSync
from inginious.frontend.pages.api._api_page import APIAuthenticatedPage
from inginious.frontend.parsable_text import ParsableText


def custom_input_notebook(client):
    """
    This function returns a CustomInputNotebookManager in charge of running the selected tests by the student to run.
    This is instead of doing a new submission whenever the student wants to check the result of some few tests.
    :param client:
    :return: CustomInputNotebookManager
    """

    class CustomInputNotebookManager(APIAuthenticatedPage):
        def __init__(self):
            self._client = client

        def add_unsaved_job(self, task, inputdata):
            temp_client = ClientSync(self._client)
            return temp_client.new_job(task, inputdata,
                                       "Test notebook - " + self.user_manager.session_username())

        def is_valid_input(self, problem_id, user_input):
            if (problem_id + "/input") not in user_input:
                return False

            # The selected tests are given as a string separated by comma
            tests = user_input[problem_id + "/input"].split(',')
            if len(tests) <= 0 or len(tests) > 3:
                return False
            return True

        def parse_selected_tests(self, user_input, problem_id, task_tests):
            """
            Returns a list of tuples that contains information about each test that the student selected, this is
            the way tests are given to the container when a normal submission is done
            Here is how this is parsed:
                [((test_name, test_id, number_of_cases), test_weight), ...]
            """
            parsed_selected_tests = []
            selected_tests = map(int, user_input[problem_id + "/input"].split(','))
            for test_idx in selected_tests:
                parsed_selected_tests.append(
                    ((task_tests[test_idx]["name"], "q{:02d}".format(test_idx), len(task_tests[test_idx]["cases"])),
                     task_tests[test_idx]["weight"]))
            return parsed_selected_tests

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
                task_tests = task._data.get("grader_test_cases", [])
                for problem_id in init_var.keys():
                    if not self.is_valid_input(problem_id, user_input):
                        return 200, json.dumps(
                            {"status": "error", "text": _("An error occurred. The request is not correctly formed.")})
                    user_input[problem_id + "/input"] = self.parse_selected_tests(user_input, problem_id, task_tests)
                result, _1, problems, tests, custom, archive, stdout, stderr = self.add_unsaved_job(task, user_input)

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

    return CustomInputNotebookManager
