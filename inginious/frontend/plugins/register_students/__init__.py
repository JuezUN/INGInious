import os
from inginious.frontend.plugins.utils import create_static_resource_page, read_file
from .pages.api.add_course_students_csv_file_api import AddCourseStudentsCsvFile

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")
_REGISTER_STUDENTS_MODAL_HTML_FILE = "register_students_modal.html"


def init(plugin_manager, _1, _2, config):
    plugin_manager.add_page(r'/register_students/static/(.*)', create_static_resource_page(_static_folder_path))
    plugin_manager.add_page("/api/addStudents/", AddCourseStudentsCsvFile)

    use_minified = config.get("use_minified", True)
    template_helper = plugin_manager._app.template_helper

    def add_register_students_template():
        renderer = template_helper.get_custom_renderer(_static_folder_path, False)
        languages = plugin_manager._app.available_languages

        if use_minified:
            template_helper.add_javascript("/register_students/static/js/register.min.js")
            template_helper.add_css("/register_students/static/css/register_students.min.css")
        else:
            template_helper.add_javascript("/register_students/static/js/register.js")
            template_helper.add_css("/register_students/static/css/register_students.css")

        return str(renderer.register_students_modal(languages))

    # Add the register_students helper to the template helper so that way, the hook is added.
    template_helper.add_other("register_students", (
        lambda **kwargs: template_helper._generic_hook('register_students', **kwargs)))

    plugin_manager.add_hook("register_students", add_register_students_template)
