# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
import os

from inginious.frontend.plugins.utils import create_static_resource_page
from inginious.frontend.plugins.contact_page.pages.api.contact_page import ContactPage

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def init(plugin_manager, _, __, plugin_config):
    plugin_manager.add_page(r'/contact_page/static/(.*)', create_static_resource_page(_static_folder_path))
    plugin_manager.add_page("/contact_page", ContactPage)
    plugin_manager.add_hook("css", lambda: "/contact_page/static/css/contact_page.css")
    plugin_manager.add_hook("javascript_footer", lambda: "/contact_page/static/js/contact_page_main.js")
    plugin_manager.add_hook("javascript_footer", lambda: "/contact_page/static/js/formulary.js")
