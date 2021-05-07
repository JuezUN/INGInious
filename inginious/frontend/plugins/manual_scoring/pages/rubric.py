# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
""" Contents all logic related with rubric """
import os

from ..constants import get_use_minify
from inginious.frontend.plugins.manual_scoring.constants import get_static_folder_path
from inginious.frontend.plugins.utils import read_json_file
from collections import OrderedDict


def get_manual_scoring_data(submission):
    """ return the comment, score and rubric status if they are storage """
    comment = ""
    score = _("No grade")
    rubric = []

    if 'manual_scoring' in submission:
        score = submission['manual_scoring']['grade']
        comment = submission['manual_scoring']['comment']
        rubric = submission['manual_scoring']['rubric_status']

    return comment, score, rubric


def get_rubric_content(user_manager):
    """ return the content of the rubric depending of the language """
    path = os.path.join(get_static_folder_path(), 'json')
    language_file = {'es': 'rubric_es.json', 'en': 'rubric.json', 'de': 'rubric.json', 'fr': 'rubric.json',
                     'pt': 'rubric.json'}
    current_language = user_manager.session_language()
    path = os.path.join(path, language_file[current_language])
    return OrderedDict(sorted(read_json_file(path).items()))


def add_static_files_to_render_notebook(template_helper):
    """ it adds js files to be able to render notebooks. Theses files are from multilang plugin  """
    template_helper.add_javascript("https://cdn.jsdelivr.net/npm/marked/marked.min.js")
    template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/prism/1.19.0/components/prism-core.min.js")
    template_helper.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/prism/1.19.0/components/prism-python.min.js")
    template_helper.add_css("https://cdnjs.cloudflare.com/ajax/libs/prism/1.19.0/themes/prism.min.css")
    if get_use_minify():
        template_helper.add_javascript("/multilang/static/notebook_renderer.min.js")
        template_helper.add_javascript("/multilang/static/multilang.min.js")
    else:
        template_helper.add_javascript("/multilang/static/notebook_renderer.js")
        template_helper.add_javascript("/multilang/static/multilang.js")
        template_helper.add_javascript("/multilang/static/grader.js")
