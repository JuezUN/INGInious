# -*- coding: utf-8 -*-
#
# This file is part of UNCode. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Rubric scoring page """

import web

from bson.objectid import ObjectId

from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.manual_scoring.pages import constants
from inginious.frontend.plugins.utils import read_json_file, get_mandatory_parameter

base_renderer_path = constants.render_path


def get_manual_scoring_data_of_submission(submission):
    """  """
    comment = ""
    score = "No grade"
    rubric = []

    if 'manual_scoring' in submission:
        score = submission['manual_scoring']['grade']
        comment = submission['manual_scoring']['comment']
        rubric = submission['manual_scoring']['rubric_status']

    return comment, score, rubric


def get_submission_result_text(submission_input):
    info = submission_input['text']
    pars_text = ParsableText(info)
    final_text = pars_text.parse()
    final_text = final_text.replace('\n', '')
    return final_text


class ManualScoringPage(INGIniousAdminPage):
    """ Rubric scoring page to manual scoring """

    def GET_AUTH(self, course_id, task_id, submission_id):
        """ Get request """
        course, task = self.get_course_and_check_rights(course_id, task_id)

        return self.render_page(course, task, submission_id)

    def POST_AUTH(self, course_id, task_id, submission_id):
        """ POST request """
        course, task = self.get_course_and_check_rights(course_id, task_id)

        self.update_manual_comment_and_grade(submission_id)

        return self.render_page(course, task, submission_id)

    def update_manual_comment_and_grade(self, submission_id):
        """ update the grade and comment on db """
        manual_grade = get_mandatory_parameter(web.input(), "manual_grade")
        comment = get_mandatory_parameter(web.input(), "comment")
        rubric_status = get_mandatory_parameter(web.input(), "rubric")
        self.database.submissions.update(
            {"_id": ObjectId(submission_id)},
            {"$set": {"manual_scoring.grade": manual_grade,
                      "manual_scoring.comment": comment,
                      "manual_scoring.rubric_status": rubric_status
                      }
             })

    def render_page(self, course, task, submission_id):
        """ Get all data and display the page """
        rubric_content = self.get_rubric_content()
        problem_id = task.get_problems()[0].get_id()
        submission = self.submission_manager.get_submission(submission_id, user_check=False)
        submission_input = self.submission_manager.get_input_from_submission(submission)
        comment, score, rubric_status = get_manual_scoring_data_of_submission(submission)

        data = {
            "url": 'manual_scoring',
            "summary": submission_input['custom']['custom_summary_result'],
            "grade": score,
            "language": submission_input['input'][problem_id + '/language'],
            "comment": comment,
            "score": submission_input['grade'],
            "task_name": course.get_task(submission_input['taskid']).get_name(self.user_manager.session_language()),
            "result": submission_input['result'],
            "feedback_result_text": get_submission_result_text(submission_input),
            "problem": submission_input['input'][problem_id],
            "username": submission_input['username'][0],
            "name": self.user_manager.get_user_realname(submission_input['username'][0]),
            "env": task.get_environment(),
            "question_id": problem_id,
            "submission_id": submission_id,
            "rubric_status": rubric_status
        }

        return (
            self.template_helper.get_custom_renderer(base_renderer_path).manual_scoring(
                course, task, rubric_content, data)
        )

    def get_rubric_content(self):
        path = 'inginious/frontend/plugins/manual_scoring/static/json/'
        language_file = {'es': 'rubric_es.json', 'en': 'rubric.json', 'de': 'rubric.json', 'fr': 'rubric.json',
                         'pt': 'rubric.json'}
        current_language = self.user_manager.session_language()
        path += language_file[current_language]

        return read_json_file(path)
