import os
import tempfile
import json
from collections import OrderedDict

from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from .grader_form import GraderForm, InvalidGraderError

_NOTEBOOK_OK_FILE_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'notebook_ok_config_file_template.txt')
_RUN_FILE_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'run_file_template.txt')
_NOTEBOOK_TEST_FILE_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'notebook_test_file_template.txt')


class NotebookForm(GraderForm):
    """
    This class manage the fields only present on the Notebook form.
    """

    def tests_to_dict(self):
        """ This method parses the tests cases information in a dictionary """
        print(self.task_data)
        # Transform grader_test_cases[] entries into an actual array (they are sent as separate keys).
        grader_test_cases = CourseEditTask.dict_from_prefix("notebook_grader_test", self.task_data) or OrderedDict()
        # Remove the repeated information
        keys_to_remove = [key for key, _ in self.task_data.items() if key.startswith("notebook_grader_test[")]
        for key in keys_to_remove:
            del self.task_data[key]

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
                test["setup_code"] = str(test.get("setup_code", ""))
            except (ValueError, TypeError):
                raise InvalidGraderError("The setup code for grader tests must be a string")

            if test["weight"] <= 0:
                raise InvalidGraderError("The weight must be a positive number")

            if not test.get("cases", None):
                raise InvalidGraderError(
                    "You must provide test cases for test " + test["name"] + " to autogenerate the grader")

            notebook_tests.append(test)

        if not notebook_tests:
            raise InvalidGraderError("You must provide tests to autogenerate the grader")

        return notebook_tests

    def parse(self):
        super(NotebookForm, self).parse()
        # Parse test cases
        self.task_data['grader_test_cases'] = self.parse_and_validate_tests()
        self.task_data["notebook_filename"] = self.task_data.get("notebook_filename", "task")

    def generate_grader(self):
        """ This method generates a grader through the form data """

        self._generate_ok_config_file()
        self._generate_run_file()
        self._generate_tests_files()

    @staticmethod
    def _parse_code_to_doctest(code):
        parsed_code = ""
        code_lines = code.split('\n')
        for index, line in enumerate(code_lines):
            parsed_code += ">>> {}".format(line.strip())
            if index + 1 < len(code_lines):
                parsed_code += "\n"
        return parsed_code

    def _parse_case(self, case):
        input_code = self._parse_code_to_doctest(case["input_code"])
        output_code = case["output_code"]
        template = """
                    {
                        'code': r\"\"\"
                        %s
                        %s
                        \"\"\",
                        'hidden': False,
                        'locked': False
                    },""" % (input_code, output_code)
        return template

    def _generate_tests_files(self):
        for test_index, test in enumerate(self.task_data["grader_test_cases"]):
            test_name = "\'{}\'".format(test["name"])
            test_weight = test["weight"]
            notebook_import_code = "from {} import *\n".format(self.task_data["notebook_filename"])
            test_setup_code = notebook_import_code + test["setup_code"]
            test_setup_code = self._parse_code_to_doctest(test_setup_code)
            test_cases = test["cases"]
            test_cases_str = ""
            for index, case in test_cases.items():
                result = self._parse_case(case)
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
        with open(_NOTEBOOK_OK_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
            ok_file_template = json.load(template)

            ok_file_name = filename + ".ok"
            target_ok_file = os.path.join(temporary, ok_file_name)
            ok_file_template["name"] = task_name
            ok_file_template["src"] = [filename_py_src]
            with open(target_ok_file, "w") as file:
                file.write(json.dumps(ok_file_template, indent=2, sort_keys=True))
            self.task_fs.copy_to(temporary)
