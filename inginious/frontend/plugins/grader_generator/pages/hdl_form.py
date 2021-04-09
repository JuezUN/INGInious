import os
import tempfile
from .grader_form import GraderForm, InvalidGraderError
from .constants import BASE_TEMPLATE_FOLDER

_HDL_FILE_TEMPLATE_PATH = os.path.join(BASE_TEMPLATE_FOLDER, 'hdl_file_template.txt')


class HDLForm(GraderForm):
    """
    This class manages the fields only present on the HDL form
    """

    def parse(self):
        super(HDLForm, self).parse()

        if not self.task_data['testbench_file_name']:
            raise InvalidGraderError(_("No testbench was selected for testing"))

        if not self.task_data['hdl_expected_output']:
            raise InvalidGraderError(_("No expected output was selected for testing"))

    def generate_grader(self):
        problem_id = self.task_data["grader_problem_id"]
        testbench_file_name = self.task_data["testbench_file_name"]
        hdl_expected_output = self.task_data["hdl_expected_output"]
        options = {
            "treat_non_zero_as_runtime_error": self.task_data["treat_non_zero_as_runtime_error"],
            "diff_max_lines": self.task_data["grader_diff_max_lines"],
            "diff_context_lines": self.task_data["grader_diff_context_lines"],
            "output_diff_for": [testbench_file_name],
            "entity_name": self.task_data.get('vhdl_entity', None)
        }

        with open(_HDL_FILE_TEMPLATE_PATH, "r") as template, tempfile.TemporaryDirectory() as temporary:
            run_file_template = template.read()

            run_file_name = 'run'
            target_run_file = os.path.join(temporary, run_file_name)

            with open(target_run_file, "w") as f:
                f.write(run_file_template.format(
                    problem_id=repr(problem_id), testbench=repr(testbench_file_name),
                    options=repr(options), output=repr(hdl_expected_output)))

            self.task_fs.copy_to(temporary)
