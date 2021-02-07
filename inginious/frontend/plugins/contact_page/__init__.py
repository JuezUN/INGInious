# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
import os

from inginious.frontend.plugins.contact_page.pages.api.slack_url_error import SlackURLError
from inginious.frontend.plugins.utils import create_static_resource_page
from inginious.frontend.plugins.contact_page.pages.api.contact_page import ContactPage, set_url_channel

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def define_slack_url(main_message_url, course_url):
    try:
        set_url_channel(main_message_url, course_url)
    except SlackURLError as e:
        print(e)


def init(plugin_manager, _, __, plugin_config):
    plugin_manager.add_page(r'/contact_page/static/(.*)', create_static_resource_page(_static_folder_path))

    use_minified = plugin_config.get("use_minified", True)
    slack_message_url = plugin_config.get("main_slack_url_message", "")
    slack_new_course_url = plugin_config.get("slack_url_for_new_course", "")

    define_slack_url(slack_message_url, slack_new_course_url)

    if use_minified:
        plugin_manager.add_hook("css", lambda: "/contact_page/static/css/contact_page.min.css")
        plugin_manager.add_hook("javascript_footer", lambda: "/contact_page/static/js/contact_page.min.js")
    else:
        plugin_manager.add_hook("css", lambda: "/contact_page/static/css/contact_page.css")
        plugin_manager.add_hook("javascript_footer", lambda: "/contact_page/static/js/contact_page_main.js")
        plugin_manager.add_hook("javascript_footer", lambda: "/contact_page/static/js/formulary.js")
        plugin_manager.add_hook("javascript_footer", lambda: "/contact_page/static/js/message_box.js")

    plugin_manager.add_page("/contact_page", ContactPage)
