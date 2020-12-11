# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" General data for all manual scoring pages """

import os

RENDERER_PATH = 'frontend/plugins/rubric_scoring/pages/templates'

BASE_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../static')


def rubric_course_admin_menu_hook(course):
    """ Add new Manual scoring item to side bar """
    return "rubric_scoring", '<i class="fa fa-table" aria-hidden="true"></i> Manual Scoring'
