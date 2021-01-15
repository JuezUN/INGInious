import os

from inginious.frontend.plugins.utils import create_static_resource_page, read_file

from .pages.data_policy import DataPolicyPage
from .pages.api.used_grading_environments import UsedGradingEnvironments
from .pages.api.used_subproblem_types import UsedSubproblemTypes
from .constants import set_used_grading_environments, set_used_subproblem_types, about_us_option_hook

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")

_CONTEXT_TASK_TEMPLATE_FILE = "context_task_template.rst"


def init(plugin_manager, course_factory, client, config):
    plugin_manager.add_page(r'/UNCode/static/(.*)', create_static_resource_page(_static_folder_path))

    use_minified = config.get("use_minified", True)
    if use_minified:
        plugin_manager.add_hook("javascript_footer", lambda: "/UNCode/static/js/UNCode.min.js")
        plugin_manager.add_hook("css", lambda: "/UNCode/static/css/UNCode.min.css")
    else:
        plugin_manager.add_hook("javascript_footer", lambda: "/UNCode/static/js/uncode.js")
        plugin_manager.add_hook("javascript_footer", lambda: "/UNCode/static/js/task_files_tab.js")
        plugin_manager.add_hook("css", lambda: "/UNCode/static/css/uncode.css")

    used_grading_environments = config.get("used_grading_environments", [])
    set_used_grading_environments(used_grading_environments)

    used_subproblem_types = config.get("used_subproblem_types", [])
    set_used_subproblem_types(used_subproblem_types)

    plugin_manager.add_page("/api/getUsedGradingEnvironments/", UsedGradingEnvironments)
    plugin_manager.add_page("/api/getUsedSubproblemTypes/", UsedSubproblemTypes)
    plugin_manager.add_page("/data_policy", DataPolicyPage)

    renderer = plugin_manager._app.template_helper.get_custom_renderer('frontend/plugins/UNCode/static', False)

    plugin_manager.add_hook("additional_body_html", lambda: "<p class='hidden' id='default_task_context'>" +
                                                            read_file(_static_folder_path,
                                                                      _CONTEXT_TASK_TEMPLATE_FILE) + "</p>")
    plugin_manager.add_hook("additional_body_html", lambda: str(renderer.task_context_help_modal()))
    plugin_manager.add_hook("additional_body_html", lambda: str(renderer.task_files_upload_multiple_modal()))
    plugin_manager.add_hook("additional_body_html", lambda: str(renderer.task_result_legend_modal()))
    plugin_manager.add_hook("additional_body_html", lambda: str(renderer.delete_all_files_confirm_modal()))

    plugin_manager.add_hook("uncode_navbar_options", lambda: str(about_us_option_hook()))
