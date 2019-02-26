# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A demo plugin that adds a page """
from . import pages


def init(plugin_manager, _, _2, _3):
    """ Init the plugin """

    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/space_visualization', pages.VisualizationCourseTaskListPage)
    plugin_manager.add_page(r'/admin/([a-z0-9A-Z\-_]+)/space_visualization/task/([a-z0-9A-Z\-_]+)', pages.SpaceVisualizationPage)
    plugin_manager.add_page(r'/static/space_visualization/(.*)',pages.StaticResourcePage)

    plugin_manager.add_hook('course_admin_menu', pages.space_visualization_course_admin_menu_hook)