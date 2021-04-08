# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" General data for all manual scoring pages """
import os

_render_path = 'frontend/plugins/manual_scoring/pages/templates'
_use_minified = True
_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def get_manual_scoring_link_code(course):
    """ Add new Manual scoring item to side bar """
    manual_scoring_str = _("Manual Scoring")
    return "manual_scoring", '<i class="fa fa-table" aria-hidden="true"></i> {manual_scoring_str}'.format(
        manual_scoring_str=manual_scoring_str)


def get_feedback_link_code(course, template_helper):
    """ return the html code to add a new link to course_menu """
    feedback_str = _("Feedback")
    return """
            <a class="list-group-item list-group-item-info"
                href="/feedback_list/{course_id}">
                <i class="fa fa-commenting" aria-hidden="true"></i>
                {feedback_str}
            </a>""".format(course_id=course.get_id(),
                           feedback_str=feedback_str)


def set_use_minified(use_minified):
    """ Define if use minified files """
    global _use_minified
    _use_minified = use_minified


def get_use_minify():
    """ return a boolean to define if use minified files """
    return _use_minified


def get_render_path():
    """ getter for render path """
    return _render_path


def get_static_folder_path():
    return _static_folder_path


def get_element_of_dict(dictionary, key):
    if key in dictionary:
        return dictionary[key], ""
    else:
        return None, key


def get_element_of_dict_double_key(dictionary, key_1, key_2):
    internal_dict, error = get_element_of_dict(dictionary, key_1)
    if internal_dict:
        return get_element_of_dict(internal_dict, key_2)
    if not error:
        error = key_1 + ": internal_dict is empty"
    return internal_dict, error


def add_error_to_list(error_list, new_error):
    if new_error != "":
        error_list.append(new_error)


def get_dict_value(dictionary, key_1, key_2=None, error_list=None):
    if key_2:
        value, error = get_element_of_dict_double_key(dictionary, key_1, key_2)
    else:
        value, error = get_element_of_dict(dictionary, key_1)
    if error_list:
        add_error_to_list(error_list, error)
    return value if value else _("Not available")
