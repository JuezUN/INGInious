# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
"""Notebooks grader serverless module"""

from .api.notebook_grader_api import NotebookGradingAPI, NotebookGradersAPI, UserRolesAPI, UserCoursesAPI, notebook_submission


def init(plugin_manager, _, __, plugin_config):
    """
        Init the plugin.
        Available configuration in configuration.yaml:
        ::

            - public_key_n: public key n value
            - public_key_e: public key e value
    """
    public_key_n = int(plugin_config.get("public_key_n"))
    public_key_e = int(plugin_config.get("public_key_e"))
    public_key = (public_key_n, public_key_e)
    plugin_manager.add_page(r"/api/user_roles", UserRolesAPI)
    plugin_manager.add_page(r"/api/user_courses", UserCoursesAPI)
    plugin_manager.add_page(r"/api/notebook_grader", NotebookGradingAPI)
    plugin_manager.add_page(r"/api/notebook_graders", NotebookGradersAPI)
    plugin_manager.add_page(r"/api/notebook_grader/submit", notebook_submission(public_key))
