import json
import web

from inginious.frontend.plugins.utils import get_mandatory_parameter
from inginious.frontend.pages.api._api_page import APIAuthenticatedPage
from inginious.frontend.parsable_text import ParsableText


def custom_input_notebook(client, custom_test_manager):
    """
    This function returns a CustomTestNotebookAPI in charge of running the selected tests by the student to run.
    This is instead of doing a new submission whenever the student wants to check the result of some few tests.
    :param client:
    :param custom_test_manager:
    :return: CustomTestNotebookAPI
    """

    class CustomTestNotebookAPI(APIAuthenticatedPage):
        def __init__(self):
            self._client = client
            self._custom_test_manager = custom_test_manager

        def _add_custom_test_job(self, task, input_data):
            return self._custom_test_manager.new_job(task, input_data,
                                                     "Custom test notebook - " + self.user_manager.session_username())

        def _is_valid_input(self, problem_id, user_input):
            if (problem_id + "/input") not in user_input:
                return False

            if not user_input[problem_id + "/input"]:
                return False

            # The selected tests are given as a string separated by comma
            tests = user_input[problem_id + "/input"].split(",")
            max_custom_tests = 3
            if len(tests) <= 0 or len(tests) > max_custom_tests:
                return False
            return True

        def _parse_selected_tests(self, user_input, problem_id, task_tests):
            """
            Returns a list of tuples that contains information about each test that the student selected, this is
            the way tests are given to the container when a normal submission is done
            Here is how this is parsed:
                [((test_name, test_id, number_of_cases), test_weight), ...]
            """
            parsed_selected_tests = [None] * len(task_tests)
            selected_tests = map(int, user_input[problem_id + "/input"].split(","))
            for test_idx in selected_tests:
                parsed_selected_tests[test_idx] = (
                    (task_tests[test_idx]["name"], "q{:02d}".format(test_idx), len(task_tests[test_idx]["cases"])),
                    task_tests[test_idx]["weight"])
            return parsed_selected_tests

        def API_GET(self):
            request_params = web.input()

            custom_test_id = get_mandatory_parameter(request_params, "custom_test_id")
            custom_test = self._custom_test_manager.get_custom_test(custom_test_id)

            if not custom_test:
                web.header("Content-Type", "application/json")
                return 404, json.dumps(
                    {"status": "error", "text": _("Custom test job not found. Try running the custom tests again.")})
            elif self._custom_test_manager.is_done(custom_test_id):
                data = {
                    "status": custom_test["status"],
                    "result": custom_test["result"],
                    "text": ParsableText(custom_test["text"]).parse(),
                }
                web.header("Content-Type", "application/json")
                self._custom_test_manager.delete_custom_test(custom_test_id)
                return 200, json.dumps(data)
            elif self._custom_test_manager.is_waiting(custom_test_id):
                web.header("Content-Type", "application/json")
                return 200, json.dumps({"status": "waiting", "text": _("Custom tests are still running.")})

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
                    if not self._is_valid_input(problem_id, user_input):
                        web.header("Content-Type", "application/json")
                        return 200, json.dumps(
                            {"status": "error",
                             "text": _("Please select at least 1 and up to 3 tests.")})
                    user_input[problem_id + "/input"] = self._parse_selected_tests(user_input, problem_id, task_tests)

                custom_test_id = self._add_custom_test_job(task, user_input)

                web.header("Content-Type", "application/json")
                return 200, json.dumps(
                    {"status": "done", "custom_test_id": custom_test_id, "text": _("Custom tests are running.")})
            except Exception as exp:
                web.header("Content-Type", "application/json")
                return 200, json.dumps({"status": "error", "text": str(exp)})

    return CustomTestNotebookAPI
