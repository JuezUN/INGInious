import os

from inginious.common.tasks_problems import FileProblem
from inginious.frontend.task_problems import DisplayableFileProblem

path_to_plugin = os.path.abspath(os.path.dirname(__file__))


class NotebookFileProblem(FileProblem):
    """Python notebook file problem"""

    def __init__(self, task, problemid, content, translations=None):
        FileProblem.__init__(self, task, problemid, content, translations)

    @classmethod
    def get_type(cls):
        return "notebook_file"


class DisplayableNotebookFileProblem(NotebookFileProblem, DisplayableFileProblem):
    """ A displayable python notebook file problem"""

    def __init__(self, task, problemid, content, translations=None):
        NotebookFileProblem.__init__(self, task, problemid, content, translations)

    @classmethod
    def get_renderer(cls, template_helper):
        """ Get the renderer for this class problem """
        return template_helper.get_custom_renderer(os.path.join(path_to_plugin, "templates"), False)

    @classmethod
    def get_type_name(cls, gettext):
        return gettext("Notebook")

    @classmethod
    def show_editbox(cls, template_helper, key):
        renderer = DisplayableNotebookFileProblem.get_renderer(template_helper)
        return renderer.notebook_file_edit(cls.get_type(), key)

    def show_input(self, template_helper, language, seed):
        renderer = DisplayableNotebookFileProblem.get_renderer(template_helper)

        task = self.get_task()
        course_id = task.get_course().get_id()
        environment = task.get_environment()
        multiple_language_render = str(renderer.notebook_file(self.get_id(), self.get_type(), course_id, environment))
        standard_code_problem_render = super(DisplayableNotebookFileProblem, self).show_input(template_helper, language,
                                                                                              seed)

        return multiple_language_render + standard_code_problem_render
