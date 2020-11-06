# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
""" Data policy page on UNCode plugin """


from inginious.frontend.pages.utils import INGIniousPage


class DataPolicyPage(INGIniousPage):
    """ Data policy page """

    def GET(self):
        """ Get request """
        return self.template_helper.get_custom_renderer("frontend/plugins/UNCode/pages/templates").data_policy()
