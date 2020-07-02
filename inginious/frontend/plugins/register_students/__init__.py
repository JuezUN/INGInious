import os
from inginious.frontend.plugins.utils import create_static_resource_page, read_file
from .pages.api.add_course_students_csv_file_api import AddCourseStudentsCsvFile

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")
_REGISTER_STUDENTS_MODAL_HTML_FILE = "register_students_modal.html"


def init(plugin_manager, course_factory, client, config):
    plugin_manager.add_page(r'/register_students/static/(.*)', create_static_resource_page(_static_folder_path))
    plugin_manager.add_page("/api/addStudents/", AddCourseStudentsCsvFile)

    use_minified = config.get("use_minified", True)
    if use_minified:
        plugin_manager.add_hook("javascript_footer", lambda: "/register_students/static/js/register.min.js")
        plugin_manager.add_hook("css", lambda: "/register_students/static/css/register_students.min.css")
    else:
        plugin_manager.add_hook("javascript_footer", lambda: "/register_students/static/js/register.js")
        plugin_manager.add_hook("css", lambda: "/register_students/static/css/register_students.css")

    renderer = plugin_manager._app.template_helper.get_custom_renderer(_static_folder_path, False)
    print(str(renderer.register_students_modal()))
    plugin_manager.add_hook("additional_body_html", lambda: str(renderer.register_students_modal()))
