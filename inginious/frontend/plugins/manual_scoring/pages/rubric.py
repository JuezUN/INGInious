""" Contents all logic related with rubric """
import os

from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.plugins.utils import read_json_file


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


def get_submission_result_text(submission_input):
    """ return the result of a submission """
    info = submission_input['text']
    pars_text = ParsableText(info)
    final_text = pars_text.parse()
    final_text = final_text.replace('\n', '')
    return final_text


def get_rubric_content(user_manager):
    """ return the content of the rubric depending of the language """
    path = 'inginious/frontend/plugins/manual_scoring/static/json/'
    language_file = {'es': 'rubric_es.json', 'en': 'rubric.json', 'de': 'rubric.json', 'fr': 'rubric.json',
                     'pt': 'rubric.json'}
    current_language = user_manager.session_language()
    path = os.path.join(path, language_file[current_language])

    return read_json_file(path)
