# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

_use_minified = True


def set_use_minified(use_minified):
    """ Define if use minified files """
    global _use_minified
    _use_minified = use_minified


def use_minified():
    """ return a boolean to define if use minified files """
    return _use_minified


def add_static_files_on_task_page(template_helper):
    if use_minified:
        template_helper.add_javascript("/code_preview/static/js/code_preview_load.min.js")
    else:
        template_helper.add_javascript("/code_preview/static/js/code_preview_load.js")
