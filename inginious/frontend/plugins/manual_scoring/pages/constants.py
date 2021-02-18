# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" General data for all manual scoring pages """

_render_path = 'frontend/plugins/manual_scoring/pages/templates'
_use_minified = True


def get_manual_scoring_link_code(course):
    """ Add new Manual scoring item to side bar """
    return "manual_scoring", '<i class="fa fa-table" aria-hidden="true"></i> Manual Scoring'


def set_use_minified(use_minified):
    """ Define if use minified files """
    global _use_minified
    _use_minified = use_minified


def get_use_minify():
    """ return a boolean to define if use minified files """
    return _use_minified


def get_render_path():
    return _render_path
