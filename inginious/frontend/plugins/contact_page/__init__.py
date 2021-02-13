# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Contact page initialization """

import os

from inginious.frontend.plugins.contact_page.pages.slack_url_error import SlackURLError
from inginious.frontend.plugins.utils import create_static_resource_page
from inginious.frontend.plugins.contact_page.pages.contact_page import ContactPage
from .pages.constants import set_url_channel, set_use_minified

_static_folder_path = os.path.join(os.path.dirname(__file__), "static")


def define_slack_url(main_message_url, course_url):
    """ define the Slack url where the messages arrive """
    try:
        set_url_channel(main_message_url, course_url)
    except SlackURLError as error:
        print(error)


def init(plugin_manager, course_factory, client, plugin_config):
    """ Init the plugin """

    plugin_manager.add_page(r'/contact_page/static/(.*)', create_static_resource_page(_static_folder_path))

    use_minified = plugin_config.get("use_minified", True)
    slack_url_contact_channel = plugin_config.get("slack_url_contact_channel", "")
    slack_url_course_creation_ch = plugin_config.get("slack_url_course_creation_channel", "")

    define_slack_url(slack_url_contact_channel, slack_url_course_creation_ch)
    set_use_minified(use_minified)

    plugin_manager.add_page("/contact_page", ContactPage)
