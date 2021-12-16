# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os

from inginious.frontend.plugins.utils import create_static_resource_page
from .pages.lti_user_manager import get_user_lti, RegisterLTIPage

_LTI_REGISTER_STATIC_FILES = os.path.join(os.path.dirname(__file__),"static")

def init(plugin_manager, course_factory, client, config):

    plugin_manager.add_page(r'/lti_register/static/(.*)', create_static_resource_page(_LTI_REGISTER_STATIC_FILES))

    plugin_manager.add_page('/register_user', RegisterLTIPage)

    plugin_manager.add_hook('lti_user_account', get_user_lti)