# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os

_TEMPLATES_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "templates")


def add_course_creation_main_menu(plugin_manager, course_factory, use_minified):
    """ Add a menu for the plagiarism checker in the administration. """

    def _get_course_id_name_tuple(course, user_manager):
        """ Return a tuple of the course id and name: (course_id, course_name). """
        try:
            return course.get_id(), course.get_name(user_manager.session_language())
        except Exception:
            return course.get_id(), course.get_id()

    def _get_courses_list():
        """ Generate a list of courses, each element is a tuple of the course id and the course object. """
        courses = course_factory.get_all_courses()
        user_manager = plugin_manager.get_user_manager()

        return list(sorted(map(lambda course: _get_course_id_name_tuple(course, user_manager), courses.values()),
                           key=lambda course: course[1]))

    def course_creation_menu(template_helper):
        """ Code to add the create course menu in the right of my courses pages. """
        user_manager = plugin_manager.get_user_manager()

        if not user_manager.user_is_superadmin():
            return None

        print("running")

        if use_minified:
            plugin_manager.add_hook("javascript_footer",
                                    lambda: "/course_creation/static/js/course_creation.min.js")
        else:
            plugin_manager.add_hook("javascript_footer", lambda: "/course_creation/static/js/course_creation.js")

        courses_list = _get_courses_list()

        create_course_str = _("Create course")
        modal_template = str(
            template_helper.get_custom_renderer(_TEMPLATES_FOLDER_PATH, layout=False).create_course_modal(
                courses_list))

        return """<div class="list-group"><h3>Create course</h3><button class="list-group-item list-group-item-info" 
        data-toggle="modal" data-target="#create_course_modal"><i class="fa fa-plus-circle fa-fw"></i>{}
        </button></div>""".format(create_course_str) + modal_template

    return course_creation_menu
