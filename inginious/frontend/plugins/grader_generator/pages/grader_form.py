class InvalidGraderError(Exception):
    """
    This class represents any error present on
    the form for the generation of the grader (check edit_task->tab grader)
    """

    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message


class GraderForm:
    """ This class parse and validates fields in the grader form, common
    in all the forms (i.e multilang, HDL) """

    def __init__(self, task_data, task_fs):
        self.task_data = task_data
        self.task_fs = task_fs

    def parse(self):
        # Convert diff_max_lines to integer if this fail the string isn't an integer
        try:
            self.task_data["grader_diff_max_lines"] = int(self.task_data.get("grader_diff_max_lines", None))
        except (ValueError, TypeError):
            raise InvalidGraderError("'Maximum diff lines' must be an integer")

        # Convert diff_context_lines to integer if this fails the string isn't an integer
        try:
            self.task_data["grader_diff_context_lines"] = int(self.task_data.get("grader_diff_context_lines", None))
        except (ValueError, TypeError):
            raise InvalidGraderError("'Diff context lines' must be an integer")

        # Parse checkboxes
        self.task_data["treat_non_zero_as_runtime_error"] = "treat_non_zero_as_runtime_error" in self.task_data

    def validate(self):
        # Check if grader problem was set
        if 'grader_problem_id' not in self.task_data:
            raise InvalidGraderError("Grader: the problem was not specified")

        # The problem_id does not exists
        if self.task_data['grader_problem_id'] not in self.task_data['problems']:
            print(self.task_data)
            raise InvalidGraderError("Grader: problem does not exist")

        # check the type of problem. (written code or project folder only options)
        problem_type = self.task_data["problems"][self.task_data["grader_problem_id"]]["type"]

        if problem_type not in ['code_multiple_languages', 'code_file_multiple_languages', 'notebook_file']:
            raise InvalidGraderError(
                "Grader: only 'Code Multiple Language', 'Code File Multiple Language' and 'Notebook' problems are supported")

        # Check values that must be positive
        if self.task_data["grader_diff_max_lines"] <= 0:
            raise InvalidGraderError("'Maximum diff lines' must be positive")

        if self.task_data["grader_diff_context_lines"] <= 0:
            raise InvalidGraderError("'Diff context lines' must be positive")
