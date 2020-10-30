# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Data policy """
from inginious.frontend.pages.utils import INGIniousPage


class DataPolicyPage(INGIniousPage):

    def GET(self):
        return self.template_helper.get_custom_renderer("frontend/plugins/UNCode/pages/templates").data_policy()