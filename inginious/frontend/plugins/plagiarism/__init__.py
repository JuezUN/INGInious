# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .plagiarism_manager import PlagiarismManagerSingleton
from .pages.plagiarism import PlagiarismPage
from .pages.plagiarism_create import PlagiarismCreate
from .pages.plagiarism_check_summary import PlagiarismCheckSummary
from .pages.plagiarism_check_download import PlagiarismCheckDownload

_STATIC_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, _, __, plugin_config):
    """
        Init the plugin.
        Available configuration in configuration.yaml:
        ::

            - plugin_module: "inginious.frontend.plugins.plagiarism"
            - storage_path: 'path/to/storage/results'
    """

    use_minified = plugin_config.get("use_minified", True)

    def add_admin_menu(course):  # pylint: disable=unused-argument
        """ Add a menu for the plagiarism checker in the administration """
        if not plugin_manager.get_user_manager().has_admin_rights_on_course(course):
            return None
        if use_minified:
            plugin_manager.add_hook("css", lambda: "/plagiarism/static/css/plagiarism.css")
        else:
            plugin_manager.add_hook("css", lambda: "/plagiarism/static/css/plagiarism.min.css")
        return "plagiarism", "<i class='fa fa-check-circle-o fa-fw'></i>&nbsp; Plagiarism"

    plugin_manager.add_page(r'/plagiarism/static/(.*)', create_static_resource_page(_STATIC_FOLDER_PATH))

    if "plagiarism_checks" not in plugin_manager.get_database().collection_names():
        plugin_manager.get_database().create_collection("plagiarism_checks")

    PlagiarismManagerSingleton(plugin_manager.get_database(), plugin_manager._app.gridfs,
                               plugin_manager.get_submission_manager(), plugin_manager.get_user_manager())

    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism', PlagiarismPage)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/create', PlagiarismCreate)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/summary/([^/]+)', PlagiarismCheckSummary)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)', PlagiarismCheckDownload)
    plugin_manager.add_page(r'/admin/([^/]+)/plagiarism/download/([^/]+)(/.*)', PlagiarismCheckDownload)

    plugin_manager.add_hook('course_admin_menu', add_admin_menu)
