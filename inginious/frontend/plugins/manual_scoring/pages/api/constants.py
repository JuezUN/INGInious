# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" General data for all manual scoring pages """

render_path = 'frontend/plugins/manual_scoring/pages/templates'


def rubric_course_admin_menu_hook(course):
    """ Add new Manual scoring item to side bar """
    return "manual_scoring", '<i class="fa fa-table" aria-hidden="true"></i> Manual Scoring'
