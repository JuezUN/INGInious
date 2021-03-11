# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import web

from inginious.frontend.pages.api._api_page import APIError
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.plugins.statistics.pages.api.user.user_api import UserApi
from inginious.frontend.plugins.utils import get_mandatory_parameter


def _transform_rst_content(content):
    """ transform the rst content """
    try:
        _check_string(content)
    except APIError as error:
        error.send()

    if not content:
        content = "**There is not content yet**\n============================"
    comment = ParsableText(content)
    return comment.parse()


def _check_string(content):
    """ Check if the content is a string """
    if not isinstance(content, str):
        raise APIError(400, "The content isn't a string")


class RstParserAPI(UserApi):
    """ api for preview rst code """
    def API_POST(self):
        """ post request """
        try:
            content = get_mandatory_parameter(web.input(), "content")
        except APIError as error:
            error.send()
            return
        comment = _transform_rst_content(content)
        return 200, comment
