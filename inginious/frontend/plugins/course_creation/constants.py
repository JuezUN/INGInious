import os

_TEMPLATES_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "templates")


def add_course_creation_main_menu(plugin_manager, course_factory):
    """ Add a menu for the plagiarism checker in the administration """

    def _get_course_id_name_tuple(course, user_manager):
        try:
            return course.get_id(), course.get_name(user_manager.session_language())
        except:
            return course.get_id(), course.get_id()

    def _get_courses_list():
        courses = course_factory.get_all_courses()
        user_manager = plugin_manager.get_user_manager()

        return list(sorted(map(lambda course: _get_course_id_name_tuple(course, user_manager), courses.values()),
                           key=lambda course: course[1]))

    def course_creation_menu(template_helper):
        user_manager = plugin_manager.get_user_manager()
        if user_manager.user_is_superadmin():
            plugin_manager.add_hook("javascript_footer", lambda: "/course_creation/static/js/course_creation.js")

            courses_list = _get_courses_list()

            create_course_str = _("Create course")
            modal_template = str(
                template_helper.get_custom_renderer(_TEMPLATES_FOLDER_PATH, layout=False).create_course_modal(
                    courses_list))

            return """<div class="list-group"><h3>Create course</h3><button class="list-group-item list-group-item-info" 
            data-toggle='modal' data-target="#create_course_modal"><i class="fa fa-plus-circle fa-fw"></i>{}
            </button></div>""".format(create_course_str) + modal_template
        else:
            return None

    return course_creation_menu
