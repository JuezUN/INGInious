import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .problems.code_multiple_languages_problem import DisplayableCodeMultipleLanguagesProblem
from .problems.code_multiple_file_languages_problem import DisplayableCodeFileMultipleLanguagesProblem
from .problems.notebook_file_problem import DisplayableNotebookFileProblem
from .problems.constants import set_linter_url, set_python_tutor_url, set_show_tools, set_use_wavedrom, set_use_minified
from .problems.custom_input import custom_input_manager_multilang
from .problems.custom_input_notebook import custom_input_notebook
from .problems.custom_test_manager import CustomTestManager

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, course_factory, client, plugin_config):
    # This option is to hide/show tools like Python tutor.
    set_show_tools(plugin_config.get("show_tools", True))
    set_use_minified(plugin_config.get("use_minified", True))
    set_use_wavedrom(plugin_config.get("use_wavedrom", False))

    python_tutor_url = plugin_config.get("python_tutor_url", "")
    if python_tutor_url != "":
        set_python_tutor_url(python_tutor_url)

    linter_url = plugin_config.get("linter_url", "")
    if linter_url != "":
        set_linter_url(linter_url)

    plugin_manager.add_page(r'/multilang/static/(.*)', create_static_resource_page(_static_folder_path))
    plugin_manager.add_page("/api/custom_input/", custom_input_manager_multilang(client))

    custom_test_manager = CustomTestManager(client, plugin_manager._user_manager, plugin_manager._database)
    plugin_manager.add_page("/api/custom_input_notebook/", custom_input_notebook(client, custom_test_manager))

    course_factory.get_task_factory().add_problem_type(DisplayableCodeMultipleLanguagesProblem)
    course_factory.get_task_factory().add_problem_type(DisplayableCodeFileMultipleLanguagesProblem)
    course_factory.get_task_factory().add_problem_type(DisplayableNotebookFileProblem)
