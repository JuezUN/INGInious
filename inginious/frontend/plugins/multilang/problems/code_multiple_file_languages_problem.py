import os
from collections import OrderedDict

from inginious.common.tasks_problems import FileProblem
from inginious.frontend.task_problems import DisplayableFileProblem
from .languages import get_all_available_languages
from .constants import get_show_tools, add_static_files

path_to_plugin = os.path.abspath(os.path.dirname(__file__))


class CodeFileMultipleLanguagesProblem(FileProblem):
    """Code file problem with multiple languages"""

    def __init__(self, task, problemid, content, translations=None):
        FileProblem.__init__(self, task, problemid, content, translations)
        self._languages = content["languages"]

    @classmethod
    def get_type(cls):
        return "code_file_multiple_languages"


class DisplayableCodeFileMultipleLanguagesProblem(CodeFileMultipleLanguagesProblem, DisplayableFileProblem):
    """ A displayable code file problem with multiple languages """

    def __init__(self, task, problemid, content, translations=None):
        CodeFileMultipleLanguagesProblem.__init__(self, task, problemid, content, translations)

    @classmethod
    def get_renderer(cls, template_helper):
        """ Get the renderer for this class problem """
        return template_helper.get_custom_renderer(os.path.join(path_to_plugin, "templates"), False)

    @classmethod
    def get_type_name(cls, gettext):
        return gettext("code file multiple languages")

    @classmethod
    def show_editbox(cls, template_helper, key):
        add_static_files(template_helper)
        renderer = DisplayableCodeFileMultipleLanguagesProblem.get_renderer(template_helper)
        return renderer.file_multilang_edit(key, get_all_available_languages())

    def show_input(self, template_helper, language, seed):
        allowed_languages = { language : get_all_available_languages()[language] for language in self._languages if language in get_all_available_languages() }
        allowed_languages = OrderedDict([(lang, allowed_languages[lang]) for lang in sorted(allowed_languages.keys())])
        dropdown_id = self.get_id() + "/language"
        custom_input_id = self.get_id() + "/input"

        renderer = DisplayableCodeFileMultipleLanguagesProblem.get_renderer(template_helper)

        task = self.get_task()
        course_id = task.get_course().get_id()
        environment = task.get_environment()

        multiple_language_render = str(
            renderer.multilang(self.get_id(), dropdown_id, allowed_languages, self.get_id(), self.get_type(),
                               task_id=self.get_task().get_id(), course_id=course_id, environment=environment, automatic_linter_option = None))
        standard_code_problem_render = super(DisplayableCodeFileMultipleLanguagesProblem, self).show_input(
            template_helper, language, seed)
        tools_render = ""
        if get_show_tools() and environment != "HDL":
            tools_render = str(
                renderer.tools(self.get_id(), "plain", custom_input_id, self.get_type(), None, None,
                               course_id=self.get_task().get_course_id()))

        add_static_files(template_helper)
        return multiple_language_render + standard_code_problem_render + tools_render
