# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
"""Notebooks grader serverless module"""

from .api.notebook_grader_api import NotebookGradingAPI, TestNotebookSubmissionAPI, UserRolesAPI


def init(plugin_manager):
    """ Init the plugin """
    plugin_manager.add_page(r"/api/user_roles", UserRolesAPI)
    plugin_manager.add_page(r"/api/notebook_grader", NotebookGradingAPI)
    plugin_manager.add_page(
        r"/api/notebook_grader/submit", TestNotebookSubmissionAPI)
