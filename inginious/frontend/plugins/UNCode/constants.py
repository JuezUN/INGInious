_used_grading_environments = []
_used_subproblem_types = []


def set_used_grading_environments(new_used_grading_environments):
    """
    Set array of used grading environments while creating/editing a task (e.g. multiple_languages)
    """
    global _used_grading_environments
    _used_grading_environments = new_used_grading_environments


def set_used_subproblem_types(new_used_subproblem_types):
    """
    Set array of used subproblem tyoes while creating/editing a task (e.g. code_multiple_languages)
    """
    global _used_subproblem_types
    _used_subproblem_types = new_used_subproblem_types


def get_used_grading_environments():
    return _used_grading_environments


def get_used_subproblem_types():
    return _used_subproblem_types
