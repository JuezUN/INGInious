import os
import tempfile
import json
import ast
from collections import OrderedDict

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from .grader_form import GraderForm, InvalidGraderError
from .constants import BASE_TEMPLATE_FOLDER

_NOTEBOOK_OK_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'notebook_ok_config_file_template.txt')
_RUN_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'run_file_template.txt')
_NOTEBOOK_TEST_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'notebook_test_file_template.txt')


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

        grader_test_cases = OrderedDict(sorted(grader_test_cases.items()))
        for index, test in grader_test_cases.items():
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

            # Strip test cases
            for case_index, case in test["cases"].items():
                case["code"] = case["code"].strip()
                case["expected_output"] = case["expected_output"].rstrip('\n')

            notebook_tests.append(test)

        if not notebook_tests:
            raise InvalidGraderError("You must provide tests to autogenerate the grader")

        return notebook_tests

    def parse(self):
        super(NotebookForm, self).parse()
        # Parse test cases
        self.task_data["notebook_filename"] = self.task_data.get("notebook_filename", "notebook").strip()
        self.task_data["notebook_setup_code_all_tests"] = self.task_data.get("notebook_setup_code_all_tests",
                                                                             "").strip()
        self.task_data['grader_test_cases'] = self.parse_and_validate_tests()

    def validate(self):
        if not _is_python_syntax_code_right(self.task_data["notebook_setup_code_all_tests"]):
            raise InvalidGraderError("Syntax error in setup code for all tests")

        for test_index, test in enumerate(self.task_data["grader_test_cases"]):
            if not _is_python_syntax_code_right(test["setup_code"]):
                raise InvalidGraderError("Syntax error in setup code of '%s' test" % test["name"])

            if test["weight"] <= 0:
                raise InvalidGraderError("The weight must be a positive number")

            if not test.get("cases", None):
                raise InvalidGraderError(
                    "You must provide test cases for test '%s' to autogenerate the grader" % test["name"])

            for case_index, case in test["cases"].items():
                if not _is_python_syntax_code_right(case["code"]):
                    raise InvalidGraderError(
                        "Syntax error in code on test '%s', case %s" % (test["name"], int(case_index) + 1))

    def generate_grader(self):
        """ This method generates a grader through the form data """

        self._generate_ok_config_file()
        self._generate_run_file()
        self._generate_ok_test_files()

    @staticmethod
    def _parse_case_to_ok_case(case):
        case_code = _parse_code_to_doctest(case["code"])
        expected_output = case["expected_output"]
        template = """{
                        'code': r\"\"\"
%s
%s
                        \"\"\",
                        'hidden': False,
                        'locked': False
                    },""" % (case_code, expected_output)
        return template

    def _get_test_setup_code(self, test):
        notebook_import_code = "from {} import *\n".format(self.task_data["notebook_filename"])
        return notebook_import_code + self.task_data["notebook_setup_code_all_tests"] + test["setup_code"]

    def _generate_ok_test_files(self):
        for test_index, test in enumerate(self.task_data["grader_test_cases"]):
            test_name = "\'{}\'".format(test["name"])
            test_weight = test["weight"]
            test_setup_code = _parse_code_to_doctest(self._get_test_setup_code(test))
            test_cases = test["cases"]
            test_cases_str = ""
            for index, case in test_cases.items():
                result = self._parse_case_to_ok_case(case)
                test_cases_str += result

            with open(_NOTEBOOK_TEST_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
                test_file_template = template.read()
                result = test_file_template \
                    .replace("{test_name}", test_name) \
                    .replace("{test_weight}", str(test_weight)) \
                    .replace("{case_data}", test_cases_str) \
                    .replace("{setup_code}", test_setup_code)

                test_filename = "q{:02d}.py".format(test_index)
                target_test_file = os.path.join(temporary, test_filename)

                with open(target_test_file, "w") as file:
                    file.write(result)

                self.task_fs.copy_to(temporary, dest="ok_tests/")

    def _generate_run_file(self):
        problem_id = self.task_data["grader_problem_id"]
        test_cases = [(test_case["name"], "q{:02d}".format(index))
                      for index, test_case in enumerate(self.task_data["grader_test_cases"])]
        weights = [test_case["weight"] for test_case in self.task_data["grader_test_cases"]]
        options = {
            "treat_non_zero_as_runtime_error": self.task_data["treat_non_zero_as_runtime_error"],
            "filename": "{}.ipynb".format(self.task_data["notebook_filename"])
        }

        with open(_RUN_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
            run_file_template = template.read()

            run_file_name = 'run'
            target_run_file = os.path.join(temporary, run_file_name)

            with open(target_run_file, "w") as f:
                f.write(run_file_template.format(
                    problem_id=repr(problem_id), test_cases=repr(test_cases),
                    options=repr(options), weights=repr(weights)))

            self.task_fs.copy_to(temporary)

    def _generate_ok_config_file(self):
        filename = self.task_data["notebook_filename"]
        filename_py_src = filename + ".py"
        task_name = self.task_data.get("name", filename)
        ok_file_name = filename + ".ok"
        with open(_NOTEBOOK_OK_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
            ok_file_template = json.load(template)
            ok_file_template["name"] = task_name
            ok_file_template["src"] = [filename_py_src]
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
    parsed_code = ""
    code_lines = [line.strip() for line in code.split('\n') if line.strip()]
    for index, line in enumerate(code_lines):
        parsed_code += ">>> {}".format(line)
        if index + 1 < len(code_lines):
            parsed_code += "\n"
    return parsed_code
