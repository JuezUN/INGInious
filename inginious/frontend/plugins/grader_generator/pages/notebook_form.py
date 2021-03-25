import os
import tempfile
import json
import ast
import re
from collections import OrderedDict
from math import ceil

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from .grader_form import GraderForm, InvalidGraderError
from .constants import BASE_TEMPLATE_FOLDER

_NOTEBOOK_OK_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'notebook_ok_config_file_template.txt')
_RUN_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'run_file_template.txt')
_NOTEBOOK_TEST_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'notebook_ok_test_file_template.txt')


class NotebookForm(GraderForm):
    """
    This class manage the fields only present on the Notebook form.
    """

    def tests_to_dict(self):
        """ This method parses the tests cases information in a dictionary """
        # Transform grader_test_cases[] entries into an actual array (they are sent as separate keys).
        grader_test_cases = CourseEditTask.dict_from_prefix("notebook_grader_test", self.task_data) or OrderedDict()
        # Remove the repeated information
        keys_to_remove = [key for key, _ in self.task_data.items() if key.startswith("notebook_grader_test[")]
        for key in keys_to_remove:
            del self.task_data[key]

        grader_test_cases = {int(key): val for key, val in grader_test_cases.items()}

        grader_test_cases = OrderedDict(sorted(grader_test_cases.items()))
        for index, test in grader_test_cases.items():
            test["cases"] = {int(key): val for key, val in test["cases"].items()}
            test["cases"] = OrderedDict(sorted(test["cases"].items()))
        return grader_test_cases

    def parse_and_validate_tests(self):
        """ This method parses all the test cases. """
        notebook_tests = []
        for index, test in self.tests_to_dict().items():
            # Parsing
            try:
                test["weight"] = float(test.get("weight", 1.0))
            except (ValueError, TypeError):
                raise InvalidGraderError("The weight for grader test cases must be a float")

            try:
                test["name"] = str(test.get("name", "q" + str(index)))
            except (ValueError, TypeError):
                raise InvalidGraderError("The name for grader tests must be a string")

            try:
                test["setup_code"] = str(test.get("setup_code", "")).strip()
            except (ValueError, TypeError):
                raise InvalidGraderError("The setup code for grader tests must be a string")

            test["show_debug_info"] = "show_debug_info" in test
            test["custom_feedback"] = test.get("custom_feedback", "")

            # Strip test cases
            for case_index, case in test["cases"].items():
                case["code"] = case["code"].strip()
                case["expected_output"] = case["expected_output"]

            notebook_tests.append(test)

        if not notebook_tests:
            raise InvalidGraderError("You must provide tests to autogenerate the grader")

        total_weights = sum([test_case["weight"] for test_case in notebook_tests])
        if total_weights <= 1e-3:
            raise InvalidGraderError(_("The sum of all weights must be grater than zero"))

        return notebook_tests

    def parse(self):
        super(NotebookForm, self).parse()
        # Parse test cases
        self.task_data["notebook_filename"] = self.task_data.get("notebook_filename", "notebook").strip()
        if not self.task_data["notebook_filename"]:
            self.task_data["notebook_filename"] = "notebook"
        self.task_data["notebook_setup_code_all_tests"] = self.task_data.get("notebook_setup_code_all_tests",
                                                                             "").strip()

        self.task_data["notebook_data_set_url"] = self.task_data.get("notebook_data_set_url", "")
        self.task_data["notebook_data_set_name"] = self.task_data.get("notebook_data_set_name", "")

        self.task_data["notebook_time_limit_test_case"] = int(
            ceil(float(self.task_data.get("notebook_time_limit_test_case", 5))))
        self.task_data["notebook_memory_limit_test_case"] = int(
            ceil(float(self.task_data.get("notebook_memory_limit_test_case", 50))))
        self.task_data['grader_test_cases'] = self.parse_and_validate_tests()

        total_cases = len(self.task_data['grader_test_cases'])
        # Additional time to calculate submission feedback.
        _additional_time_limit = 20
        # Update the grading container time and memory limit depending on amount of tests.
        self.task_data['limits']['time'] = total_cases * self.task_data[
            'notebook_time_limit_test_case'] + _additional_time_limit
        self.task_data['limits']['memory'] = self.task_data[
            'notebook_memory_limit_test_case']

    def validate(self):
        super(NotebookForm, self).validate()
        if not _is_python_syntax_code_right(self.task_data["notebook_setup_code_all_tests"]):
            raise InvalidGraderError("Grader: Syntax error in setup code for all tests")

        url_pattern = re.compile(
            r'^(?:http)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        filename_pattern = re.compile(r'[\w,\s-]+\.[A-Za-z]+')

        if self.task_data["notebook_data_set_url"]:
            if not re.match(url_pattern, self.task_data["notebook_data_set_url"]):
                raise InvalidGraderError("Grader: Dataset url is not a valid URL.")
            if not self.task_data["notebook_data_set_name"]:
                raise InvalidGraderError("Grader: To download a dataset, you must also set the dataset filename.")

        if self.task_data["notebook_data_set_name"]:
            if not re.match(filename_pattern, self.task_data["notebook_data_set_name"]):
                raise InvalidGraderError("Grader: Dataset filename is not a valid name.")
            if not self.task_data["notebook_data_set_url"]:
                raise InvalidGraderError("Grader: To download a dataset, you must also set the dataset URL.")

        if self.task_data["notebook_time_limit_test_case"] < 1:
            raise InvalidGraderError("Grader: Time limit for test cases must be positive and integer.")

        if self.task_data["notebook_time_limit_test_case"] > 30:
            raise InvalidGraderError("Grader: Time limit exceeds the maximum allowed (30 s.).")

        if self.task_data["notebook_memory_limit_test_case"] < 1:
            raise InvalidGraderError("Grader: Memory limit for test cases must be positive and integer")

        if self.task_data["notebook_memory_limit_test_case"] > 600:
            raise InvalidGraderError("Grader: Memory limit exceeds the maximum allowed (600 MBs).")

        for test_index, test in enumerate(self.task_data["grader_test_cases"]):
            if not _is_python_syntax_code_right(test["setup_code"]):
                raise InvalidGraderError("Grader: Syntax error in setup code of '%s' test" % test["name"])

            if test["weight"] <= 0:
                raise InvalidGraderError("Grader: The weight must be a positive number")

            if not test.get("cases", None):
                raise InvalidGraderError(
                    "Grader: You must provide test cases for test '%s' to autogenerate the grader" % test["name"])

            for case_index, case in test["cases"].items():
                if not _is_python_syntax_code_right(case["code"]):
                    raise InvalidGraderError(
                        "Grader: Syntax error in code on test '%s', case %s" % (test["name"], int(case_index) + 1))

    def generate_grader(self):
        """ This method generates a grader through the form data """

        self._generate_ok_config_file()
        self._generate_run_file()
        self._generate_ok_test_files()

    @staticmethod
    def _parse_case_to_ok_suite(case, setup_code):
        case_code = _parse_code_to_doctest(case["code"]).replace('"""', "'''")
        expected_output = case["expected_output"]
        suite_template = """{
                'cases': [
                    {case_data}
                ],
                'scored': True,
                'setup': r\"\"\"
{setup_code}
                \"\"\",
                'teardown': '',
                'type': 'doctest'
        },"""
        case_template = """{
                        'code': r\"\"\"
%s
%s
                        \"\"\",
                        'hidden': False,
                        'locked': False
                    },""" % (case_code, expected_output)
        return suite_template.replace("{case_data}", case_template).replace("{setup_code}", setup_code)

    def _get_test_setup_code(self, test):
        notebook_import_code = "from {} import *".format(self.task_data["notebook_filename"])
        return "%s\n%s\n%s" % (
            notebook_import_code, self.task_data["notebook_setup_code_all_tests"], test["setup_code"])

    def _generate_ok_test_files(self):
        for test_index, test in enumerate(self.task_data["grader_test_cases"]):
            test_name = "\'{}\'".format(test["name"].replace('\'', '\\\''))
            test_weight = test["weight"]
            test_setup_code = _parse_code_to_doctest(self._get_test_setup_code(test)).replace('"""', "'''")
            test_cases = test["cases"]
            test_suites_str = ""
            for index, case in test_cases.items():
                result = self._parse_case_to_ok_suite(case, test_setup_code)
                test_suites_str += '\n' + result

            with open(_NOTEBOOK_TEST_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
                test_file_template = template.read()
                result = test_file_template \
                    .replace("{test_name}", test_name) \
                    .replace("{test_weight}", str(test_weight)) \
                    .replace("{test_suites}", test_suites_str)

                test_filename = "q{:02d}.py".format(test_index)
                target_test_file = os.path.join(temporary, test_filename)

                with open(target_test_file, "w") as file:
                    file.write(result)

                self.task_fs.copy_to(temporary, dest="ok_tests/")

    def _generate_run_file(self):
        time = self.task_data["notebook_time_limit_test_case"]
        problem_id = self.task_data["grader_problem_id"]
        tests = [(test["name"], "q{:02d}".format(index), len(test["cases"])) for index, test in
                 enumerate(self.task_data["grader_test_cases"])]
        weights = [test_case["weight"] for test_case in self.task_data["grader_test_cases"]]
        options = {
            "treat_non_zero_as_runtime_error": self.task_data["treat_non_zero_as_runtime_error"],
            "filename": "{}".format(self.task_data["notebook_filename"]),
            "show_debug_info_for": [index for index, test_case in enumerate(self.task_data["grader_test_cases"])
                                    if test_case["show_debug_info"]],
            "custom_feedback": {index: test_case["custom_feedback"] for index, test_case in
                                enumerate(self.task_data["grader_test_cases"]) if
                                test_case["custom_feedback"] and test_case["show_debug_info"]},
            "time_limit": time,
            "hard_time_limit": time * 2 + 5,
            "memory_limit": self.task_data["notebook_memory_limit_test_case"],
            "dataset": {"url": self.task_data["notebook_data_set_url"],
                        "filename": self.task_data["notebook_data_set_name"]}
        }

        with open(_RUN_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
            run_file_template = template.read()

            run_file_name = 'run'
            target_run_file = os.path.join(temporary, run_file_name)

            with open(target_run_file, "w") as f:
                f.write(run_file_template.format(
                    problem_id=repr(problem_id), test_cases=repr(tests),
                    options=repr(options), weights=repr(weights)))

            self.task_fs.copy_to(temporary)

    def _generate_ok_config_file(self):
        filename = self.task_data["notebook_filename"]
        filename_py_src = "{}.py".format(filename)
        task_name = self.task_data.get("name", filename)
        ok_file_name = filename + ".ok"
        with open(_NOTEBOOK_OK_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
            ok_file_template = json.load(template)
            ok_file_template["name"] = task_name
            ok_file_template["src"] = ["/task/student/" + filename_py_src]
            target_ok_file = os.path.join(temporary, ok_file_name)

            with open(target_ok_file, "w") as file:
                file.write(json.dumps(ok_file_template, indent=2, sort_keys=True))
            self.task_fs.copy_to(temporary)


def _is_python_syntax_code_right(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        return False


def _parse_code_to_doctest(code):
    parsed_code = []
    # Parse the code in a Abstract Syntax Tree to parse correctly the code
    parser = ast.parse(code)
    # Generate a set with line numbers of lines that must start with a '>>>'.
    # This let us know the code that uses more than une line.
    main_lines = {child_node.lineno - 1 for child_node in parser.body}
    code_lines = code.split('\n')
    for index, line in enumerate(code_lines):
        if index not in main_lines:
            parsed_code.append("... {}".format(line))
        elif line:
            parsed_code.append(">>> {}".format(line))
        if index + 1 < len(code_lines):
            parsed_code.append("\n")
    return ''.join(parsed_code)
