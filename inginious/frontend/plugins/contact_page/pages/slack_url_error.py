# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Errors with Slack url """


class SlackURLError(ValueError):
    """ Error getting main slack url """

    def __init__(self, message, *args):
        super().__init__(message, *args)
