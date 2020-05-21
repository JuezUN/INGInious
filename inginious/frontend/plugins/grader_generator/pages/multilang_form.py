import os
import tempfile
from math import ceil

from collections import OrderedDict
from .grader_form import GraderForm, InvalidGraderError
from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from .constants import BASE_TEMPLATE_FOLDER

_MULTILANG_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'run_file_template.txt')


class MultilangForm(GraderForm):
    """
    This class manage the fields only present on the multilang form.
    """

    def tests_to_dict(self):
        """ This method parses the tests cases information in a dictionary """

        # Transform grader_test_cases[] entries into an actual array (they are sent as separate keys).
        grader_test_cases = CourseEditTask.dict_from_prefix("grader_test_cases", self.task_data) or OrderedDict()

        # Remove the repeated information
        keys_to_remove = [key for key, _ in self.task_data.items() if key.startswith("grader_test_cases[")]
        for key in keys_to_remove:
            del self.task_data[key]

        # Order test cases to load them correctly
        grader_test_cases = OrderedDict(sorted(grader_test_cases.items(), key=lambda test: test[1]["input_file"]))
        return grader_test_cases

    def parse_and_validate_test_cases(self):
        """ This method parses all the test cases. """
        test_cases = []
        for _, test_case in self.tests_to_dict().items():
            # Parsing
            try:
                test_case["weight"] = float(test_case.get("weight", 1.0))
            except (ValueError, TypeError):
                raise InvalidGraderError("The weight for grader test cases must be a float")

            test_case["diff_shown"] = "diff_shown" in test_case

            # Validate
            if not test_case.get("input_file", None):
                raise InvalidGraderError("Invalid input file in grader test case")

            if not test_case.get("output_file", None):
                raise InvalidGraderError("Invalid output file in grader test case")

            if not self.task_fs.exists(test_case["input_file"]):
                raise InvalidGraderError("Grader input file does not exist: " + test_case["input_file"])

            if not self.task_fs.exists(test_case["output_file"]):
                raise InvalidGraderError("Grader output file does not exist: " + test_case["output_file"])

            test_cases.append(test_case)

        if not test_cases:
            raise InvalidGraderError("You must provide test cases to autogenerate the grader")

        input_files_are_unique = (len(set(test_case["input_file"] for test_case in test_cases)) ==
                                  len(test_cases))

        if not input_files_are_unique:
            raise InvalidGraderError("Duplicated input files in grader")

        return test_cases

    def parse(self):
        super(MultilangForm, self).parse()
        # Parse test cases
        self.task_data['grader_test_cases'] = self.parse_and_validate_test_cases()
        total_cases = len(self.task_data['grader_test_cases'])
        self.task_data['time_limit_test_case'] = int(ceil(float(self.task_data.get("time_limit_test_case", 2))))
        self.task_data['memory_limit_test_case'] = int(ceil(float(self.task_data.get("memory_limit_test_case", 50))))
        self.task_data['output_limit_test_case'] = int(ceil(float(self.task_data.get("output_limit_test_case", 2))))

        # Additional time to calculate submission feedback.
        _additional_time_limit = 15
        # Additional memory to calculate submission feedback.
        _additional_memory_limit = 70
        # Update the grading container time and memory limit depending on amount of tests.
        self.task_data['limits']['time'] = total_cases * self.task_data['time_limit_test_case'] + _additional_time_limit
        self.task_data['limits']['memory'] = total_cases * self.task_data['output_limit_test_case'] + \
                                             _additional_memory_limit

    def generate_grader(self):
        """ This method generates a grader through the form data """

        problem_id = self.task_data["grader_problem_id"]
        test_cases = [(test_case["input_file"], test_case["output_file"])
                      for test_case in self.task_data["grader_test_cases"]]
        weights = [test_case["weight"] for test_case in self.task_data["grader_test_cases"]]
        time = self.task_data["time_limit_test_case"]
        # Set output limit in Bytes
        output_limit = (2 ** 20) * self.task_data["output_limit_test_case"]
        options = {
            "treat_non_zero_as_runtime_error": self.task_data["treat_non_zero_as_runtime_error"],
            "diff_max_lines": self.task_data["grader_diff_max_lines"],
            "diff_context_lines": self.task_data["grader_diff_context_lines"],
            "output_diff_for": [test_case["input_file"] for test_case in self.task_data["grader_test_cases"]
                                if test_case["diff_shown"]],
            "time_limit": time,
            "hard_time_limit": time,
            "output_limit": output_limit,
            "memory_limit": self.task_data["memory_limit_test_case"]
        }

        with open(_MULTILANG_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
            run_file_template = template.read()

            run_file_name = 'run'
            target_run_file = os.path.join(temporary, run_file_name)

            with open(target_run_file, "w") as f:
                f.write(run_file_template.format(
                    problem_id=repr(problem_id), test_cases=repr(test_cases),
                    options=repr(options), weights=repr(weights)))

            self.task_fs.copy_to(temporary)
