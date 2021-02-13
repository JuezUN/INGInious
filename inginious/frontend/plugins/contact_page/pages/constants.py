# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Define the constants elements """

from inginious.frontend.plugins.contact_page.pages.slack_url_error import SlackURLError

_url_channel = {
    "subject-comment": "",
    "subject-new-course": "",
}
_subject_new_course_id = "subject-new-course"
_use_minified = True


def set_url_channel(main_message_channel, new_course_channel):
    """ Define the URL directions where do the request """
    if main_message_channel != "":
        _url_channel["subject-comment"] = main_message_channel
        if new_course_channel != "":
            _url_channel["subject-new-course"] = new_course_channel
        else:
            _url_channel["subject-new-course"] = main_message_channel
    else:
        raise SlackURLError("The main slack's URL is empty")


def set_use_minified(use_minified):
    """ Define if use minified files """
    global _use_minified
    _use_minified = use_minified


def get_url_channel():
    """ return the url dictionary """
    return _url_channel


def get_subject_new_course_id():
    """ return the id of new course subject """
    return _subject_new_course_id


def get_use_minify():
    """ return a boolean to define if use minified files """
    return _use_minified
